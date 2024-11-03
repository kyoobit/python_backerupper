import logging
import tarfile

from datetime import datetime, timezone
from pathlib import Path


class BackerUpper:

    def __call__(self, *args, **kwargs):
        if not args and not kwargs:
            raise ValueError("No arguments passed")
        kwargs.update(source=self.resolve_source(**kwargs))
        kwargs.update(archive=self.resolve_destination(**kwargs))
        self.move_previous_archives(**kwargs)
        self.create_archive(**kwargs)
        self.remove_previous_archives(**kwargs)

    def create_archive(self, **kwargs):
        """Create a tar archive of the source file/directory at the destination

        source <str>: path to the source file or directory

        archive <str>: path to the destination archive
        """
        source = kwargs.get("source")
        archive = kwargs.get("archive")
        # Use 'w:gz' to create a compressed (.tgz) archive
        if str(archive).endswith("tgz"):
            mode = "w:gz"
        # Use 'w' to create an uncompressed (.tar) archive
        else:
            mode = "w"
        logging.debug(f"Creating archive: {archive}")
        with tarfile.open(archive, mode) as tar:
            tar.add(source)
        logging.info(f"Created archive: {archive.name}")

    def gather_matching_archives(self, **kwargs) -> tuple:
        """Gather matching archives at the destination path
        Return a (str, list) of pattern and a list of matching Paths

        *args:
        archive <Path>: The resolved archive path
        """
        archive = kwargs.get("archive")
        # Split the archive name into parts
        # example.log.2024-11-03T09-43-23-1234Z.tgz ---> ['example.log', ..., 'tgz']
        # example.log.1.tgz ---> ['example.log', ..., 'tgz']
        parts = archive.name.rsplit(".", 2)
        pattern = ".".join([parts[0], "*", parts[-1]])
        logging.debug(f"BackerUpper - Match archives with pattern: {pattern}")
        archives = list(Path(archive.parent).glob(pattern))
        logging.debug(f"BackerUpper - Matching archives: {len(archives)}")
        return pattern, archives

    def move_previous_archives(self, **kwargs):
        """Move previous archive files found at the destination path

        sequential <bool>: Use sequential (integer) instead of date+time as a marker
        """
        sequential = kwargs.get("sequential", False)
        logging.debug(f"BackerUpper - sequential: {sequential}")

        # When sequential is not used, no need to move (rename) previous archives
        if not sequential:
            logging.debug(f"BackerUpper - sequential is {sequential}, nothing to do.")
            return None

        # Gather matching archives at the destination path
        pattern, archives = self.gather_matching_archives(**kwargs)

        # No need to rotate when no archives matched the pattern
        if not archives:
            logging.debug(f"BackerUpper - No matches for: {pattern}, nothing to do.")
            return None

        # Sort is lame and will order: item.1.tgz, item.10.tgz, item.2.tgz, ...
        # Work around this by extracting the integer from the item name and
        # sorting by the integer
        items = []
        for item in archives:
            parts = item.name.rsplit(".", 2)
            items.append((int(parts[1]), item))
        # Reverse sort the list of archives, largest number to smallest
        items_ordered = sorted(items, key=lambda i: i[0], reverse=True)
        archives = [i[1] for i in items_ordered]
        # Iterate over the archives, largest number to smallest
        # example.101.tgz ---> example.102.tgz
        # example.11.tgz ---> example.12.tgz
        # example.1.tgz ---> example.2.tgz
        for item in archives:
            parts = item.name.rsplit(".", 2)
            parts[1] = str(int(parts[1]) + 1)
            new_name = Path(f"{item.parent}/{'.'.join(parts)}").resolve()
            logging.debug(f"Renaming archive: {item.name} to: {new_name.name}")
            Path(item).rename(new_name)

    def remove_previous_archives(self, **kwargs):
        """Remove previous archives according to the retention argument

        *args:
        retention_count <int>: Maximum number of archive backups to retain
        """
        retention_count = int(kwargs.get("retention_count", 10))
        logging.debug(f"BackerUpper - retention_count: {retention_count}")

        # When the retention count is zero or less there is nothing to do.
        # If you want to complain that zero should remove all backups (keep
        # zero backups) you should just not run any backups, good day to you.
        if retention_count <= 0:
            logging.debug(
                f"BackerUpper - Retention count is {retention_count}, nothing to do."
            )
            return None

        # Gather matching archives at the destination path
        pattern, archives = self.gather_matching_archives(**kwargs)

        # When archive count does not exceed the retention count, do nothing.
        if len(archives) <= retention_count:
            logging.debug(
                f"BackerUpper - Retention count is {retention_count}, nothing to do."
            )
            return None

        # When sequential
        if kwargs.get("sequential", False):
            # Sort is lame and will order: item.1.tgz, item.10.tgz, item.2.tgz, ...
            # Work around this by extracting the integer from the item name and
            # sorting by the integer
            items = []
            for item in archives:
                parts = item.name.rsplit(".", 2)
                items.append((int(parts[1]), item))
            # Reverse sort the list of archives, largest number to smallest
            items_ordered = sorted(items, key=lambda i: i[0])
            archives = [i[1] for i in items_ordered]
        # When date+time (default), reverse sort
        else:
            archives = sorted(archives, reverse=True)

        logging.info(
            f"BackerUpper - Found {len(archives)} archives matching: {pattern}"
        )
        for item in archives[0:retention_count]:
            logging.debug(f"BackerUpper - keep: {item.name}")
        for item in archives[retention_count:]:
            logging.info(f"BackerUpper - Removing archive: {item.name}")
            item.unlink()

    def resolve_destination(self, **kwargs):
        """Resolve the archive destination path

        source <str>: path to the source file or directory

        destination <str>: path to the destination archive

        sequential <bool>: Use sequential integer markers
            UTC date+time marker is used when False
            default: False

        uncompressed <bool>: Create an uncompressed tar archive
            GZIP compression is used when False
            default: False
        """
        # Use the source name
        source = kwargs.get("source")

        # Default to using the parent of the source when a destination was not provided
        destination = kwargs.get("destination", source.parent)
        if not isinstance(destination, Path):
            destination = Path(destination).expanduser().resolve()

        # A sequential marker will always use 1
        if kwargs.get("sequential", False):
            marker = 1
        # A UTC date+time marker is the default
        else:
            marker = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H-%M-%S-%fZ")

        # The extension is determined by the use of compression
        if kwargs.get("uncompressed", False):
            ext = "tar"
        else:
            ext = "tgz"

        # Combine the destination, source name, marker, and extension
        # /path/to/destination/archive.2024-11-03T07-17-02.tgz
        # /path/to/destination/archive.1.tar
        archive = Path(f"{destination}/{source.name}.{marker}.{ext}").resolve()
        logging.debug(f"BackerUpper - Resolved destination archive: {archive}")
        return archive

    def resolve_source(self, **kwargs):
        """Resolve the source path
        Raise a FileNotFoundError exception if the source does not exist

        source <str>: Source file/directory to create an archive backup from
        """
        source = Path(kwargs.get("source")).expanduser().resolve(strict=True)
        logging.debug(f"BackerUpper - Resolved source: {source}")
        return source
