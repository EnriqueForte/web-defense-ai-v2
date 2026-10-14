"""Verify a known backup into a new isolated directory; never replace live data."""
import argparse
from contextlib import closing
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path, PurePosixPath
import re
import sqlite3
import stat
import sys
from zipfile import BadZipFile, ZipFile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from scripts.backup_operational import PROFILES, DIAGNOSTIC_FILES, checked_path, verify_restore
from dashboard.services.structured_publication import GENERATION, load_current
from agents.evidence_contracts import ContractError

MAX_FILES = 10000
MAX_FILE_BYTES = 64 * 1024 * 1024
MAX_TOTAL_BYTES = 1024 * 1024 * 1024


def portable_name(name):
    if (not isinstance(name, str) or not name or '\\' in name or ':' in name
            or PurePosixPath(name).is_absolute() or PurePosixPath(name).as_posix() != name):
        raise ValueError('invalid_backup_path')
    for part in PurePosixPath(name).parts:
        if (part in {'.', '..'} or part.rstrip(' .') != part
                or re.fullmatch(r'(?:CON|PRN|AUX|NUL|COM[1-9]|LPT[1-9])(?:\..*)?', part, re.I)):
            raise ValueError('invalid_backup_path')


def expected_kind(name, profiles, *, missing=False):
    portable_name(name)
    for profile in profiles:
        definition = PROFILES[profile]
        if name == definition['log']:
            return 'file'
        if name == definition['db']:
            return 'sqlite'
        reports = definition['reports']
        if missing and name == reports:
            return 'directory'
        if not name.startswith(reports + '/'):
            continue
        local = PurePosixPath(name[len(reports) + 1:])
        if any(part.startswith('.') for part in local.parts):
            raise ValueError('unexpected_backup_file')
        if local.suffix == '.md':
            return 'file'
        if (len(local.parts) == 3 and local.parts[0] == 'analysis-diagnostics'
                and GENERATION.fullmatch(local.parts[1]) and local.parts[2] in DIAGNOSTIC_FILES):
            return 'file'
        if (local.as_posix() == 'structured/current.json' or
                (len(local.parts) == 4 and local.parts[:2] == ('structured', 'generations')
                 and GENERATION.fullmatch(local.parts[2]) and local.parts[3] in {'manifest.json', 'result.json'})):
            return 'file'
    raise ValueError('unexpected_backup_file')


def validate_manifest(manifest):
    if (type(manifest) is not dict or set(manifest) != {'schema', 'profiles', 'created_at', 'missing', 'verified', 'files'}
            or manifest['schema'] != 'web-defense-ai.backup.v1' or manifest['verified'] is not True):
        raise ValueError('unverified_backup_manifest')
    profiles = manifest['profiles']
    if (type(profiles) is not list or not profiles or any(type(p) is not str or p not in PROFILES for p in profiles)
            or len(profiles) != len(set(profiles))):
        raise ValueError('invalid_backup_profiles')
    if not isinstance(manifest['created_at'], str) or len(manifest['created_at']) > 100:
        raise ValueError('invalid_backup_metadata')
    files = manifest['files']
    if type(files) is not dict or not 1 <= len(files) <= MAX_FILES:
        raise ValueError('backup_file_limit')
    aliases, total = set(), 0
    for name, entry in files.items():
        kind = expected_kind(name, profiles)
        # Reject Windows aliases even when reviewing the same archive on Linux.
        if name.casefold() in aliases:
            raise ValueError('duplicate_backup_path')
        aliases.add(name.casefold())
        if (type(entry) is not dict or set(entry) != {'bytes', 'sha256', 'kind'} or entry['kind'] != kind
                or type(entry['bytes']) is not int or not 0 <= entry['bytes'] <= MAX_FILE_BYTES
                or not isinstance(entry['sha256'], str) or not re.fullmatch(r'[a-f0-9]{64}', entry['sha256'])):
            raise ValueError('invalid_backup_entry')
        total += entry['bytes']
    if total > MAX_TOTAL_BYTES:
        raise ValueError('backup_byte_limit')
    if type(manifest['missing']) is not list or len(manifest['missing']) > 6:
        raise ValueError('invalid_backup_missing')
    for name in manifest['missing']:
        expected_kind(name, profiles, missing=True)
        if name in files:
            raise ValueError('inconsistent_backup_missing')


def read_manifest(path):
    with path.open('rb') as stream:
        body = stream.read(4 * 1024 * 1024 + 1)
    if len(body) > 4 * 1024 * 1024:
        raise ValueError('manifest_byte_limit')
    def unique_pairs(pairs):
        result = {}
        for key, value in pairs:
            if key in result:
                raise ValueError('duplicate_manifest_key')
            result[key] = value
        return result
    return json.loads(body.decode('utf-8'), object_pairs_hook=unique_pairs), hashlib.sha256(body).hexdigest()


def review_archive(archive, manifest):
    with ZipFile(archive) as zipped:
        members = zipped.infolist()
        if len(members) != len(manifest['files']) or {m.filename for m in members} != set(manifest['files']):
            raise ValueError('archive_manifest_mismatch')
        for member in members:
            mode = stat.S_IFMT(member.external_attr >> 16)
            if (member.is_dir() or member.flag_bits & 1 or mode not in {0, stat.S_IFREG}
                    or member.file_size != manifest['files'][member.filename]['bytes']):
                raise ValueError('invalid_archive_member')


def inspect_restored(destination, profiles):
    summary = {}
    for profile in profiles:
        definition = PROFILES[profile]
        db_path = checked_path(destination, definition['db'])
        row = {'database': 'absent', 'structured_publication': 'absent'}
        if db_path.exists():
            with closing(sqlite3.connect(db_path.resolve().as_uri() + '?mode=ro', uri=True)) as db:
                db.execute('PRAGMA query_only=ON')
                db.execute('PRAGMA trusted_schema=OFF')
                if db.execute('PRAGMA integrity_check').fetchall() != [('ok',)]:
                    raise ValueError('restored_database_integrity')
                tables = dict(db.execute("SELECT name,type FROM sqlite_master WHERE name IN ('jobs','deliveries')"))
                if tables != {'jobs': 'table', 'deliveries': 'table'}:
                    raise ValueError('unexpected_restored_schema')
                row.update(database='verified', jobs=dict(db.execute('SELECT status,count(*) FROM jobs GROUP BY status')),
                           deliveries=dict(db.execute('SELECT status,count(*) FROM deliveries GROUP BY status')))
                if any(row['jobs'].get(status, 0) for status in ('queued', 'running')):
                    raise ValueError('restored_active_jobs')
        structured = checked_path(destination, definition['reports'] + '/structured')
        if (structured / 'current.json').exists():
            manifest, _, _ = load_current(structured)
            row.update(structured_publication='verified', generation=manifest['generation'])
        summary[profile] = row
    return summary


def restore(backup_directory, *, root=ROOT):
    # No caller-selected destination: all recovered data stays in a new tree.
    source = Path(backup_directory).absolute()
    for part in (source, *source.parents):
        if part.is_symlink() or (part.exists() and getattr(part.lstat(), 'st_file_attributes', 0) & 1024):
            raise ValueError('linked_backup_path')
    manifest_path = checked_path(source, 'manifest.json')
    archive = checked_path(source, 'operational.zip')
    manifest, manifest_digest = read_manifest(manifest_path)
    validate_manifest(manifest)
    review_archive(archive, manifest)
    root = Path(root).absolute()
    stamp = datetime.now(timezone.utc).strftime('restore-%Y%m%dT%H%M%S%fZ')
    destination = checked_path(root, '.local-state/recovery/' + stamp)
    verify_restore(archive, manifest, destination)
    summary = inspect_restored(destination, manifest['profiles'])
    result = {'schema': 'web-defense-ai.restore.v1', 'verified': True,
              'files': len(manifest['files']), 'missing': manifest['missing'], 'profiles': summary,
              'manifest_sha256': manifest_digest,
              'scope': 'isolated_application_data_no_live_replacement_no_delivery_replay'}
    (destination / 'recovery-review.json').write_text(json.dumps(result, indent=2), encoding='utf-8')
    return destination, result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--backup', type=Path, required=True, help='directory with operational.zip and manifest.json')
    args = parser.parse_args()
    try:
        destination, result = restore(args.backup)
        print(json.dumps({'destination': str(destination), **result}, indent=2))
        return 0
    except (OSError, ValueError, KeyError, TypeError, sqlite3.Error, BadZipFile, ContractError, RuntimeError, RecursionError) as error:
        print(f'Recuperación no verificada ({type(error).__name__}); conserva la copia y revisa su estado.', file=sys.stderr)
        return 1


if __name__ == '__main__':
    raise SystemExit(main())
