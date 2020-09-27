import posixpath

from typing import Optional, Iterable, IO, Tuple
from abc import ABCMeta, abstractmethod
from dataclasses import dataclass
from datetime import datetime

from enum import Enum


class FileType(Enum):
    DIRECTORY = 1
    FILE = 2


@dataclass(frozen=True)
class FileInfo:
    file_type: FileType
    size: int
    access_time: Optional[datetime] = None
    modify_time: Optional[datetime] = None
    create_time: Optional[datetime] = None


class FileSystem(metaclass=ABCMeta):
    @property
    @abstractmethod
    def name(self) -> str:
        ...

    @abstractmethod
    def open(self, path: str, mode: str = "r") -> IO:
        """
        Open a file

        Parameters
        ----------
        path
            Path to the file
        mode
            Required support at least of `r`,`b` modes
        Returns
        -------
        IOBase
        """
        ...

    @abstractmethod
    def exists(self, path: str) -> bool:
        ...

    @abstractmethod
    def isfile(self, path: str) -> bool:
        ...

    @abstractmethod
    def isdir(self, path: str) -> bool:
        ...

    @abstractmethod
    def info(self, path: str) -> FileInfo:
        ...

    @abstractmethod
    def ls(self, path: str) -> Iterable[Tuple[str, Optional[FileInfo]]]:
        ...

    @abstractmethod
    def walk(self, base_path: str) -> Iterable[Tuple[str, Optional[FileInfo]]]:
        ...

    def join(self, *p) -> str:
        return posixpath.join(*p)
