from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class VerifyRequest(_message.Message):
    __slots__ = ("user", "card_number", "items")
    class User(_message.Message):
        __slots__ = ("name", "contact")
        NAME_FIELD_NUMBER: _ClassVar[int]
        CONTACT_FIELD_NUMBER: _ClassVar[int]
        name: str
        contact: str
        def __init__(self, name: _Optional[str] = ..., contact: _Optional[str] = ...) -> None: ...
    class Item(_message.Message):
        __slots__ = ("name", "quantity")
        NAME_FIELD_NUMBER: _ClassVar[int]
        QUANTITY_FIELD_NUMBER: _ClassVar[int]
        name: str
        quantity: int
        def __init__(self, name: _Optional[str] = ..., quantity: _Optional[int] = ...) -> None: ...
    USER_FIELD_NUMBER: _ClassVar[int]
    CARD_NUMBER_FIELD_NUMBER: _ClassVar[int]
    ITEMS_FIELD_NUMBER: _ClassVar[int]
    user: VerifyRequest.User
    card_number: str
    items: _containers.RepeatedCompositeFieldContainer[VerifyRequest.Item]
    def __init__(self, user: _Optional[_Union[VerifyRequest.User, _Mapping]] = ..., card_number: _Optional[str] = ..., items: _Optional[_Iterable[_Union[VerifyRequest.Item, _Mapping]]] = ...) -> None: ...

class VerifyResponse(_message.Message):
    __slots__ = ("is_valid", "message")
    IS_VALID_FIELD_NUMBER: _ClassVar[int]
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    is_valid: bool
    message: str
    def __init__(self, is_valid: bool = ..., message: _Optional[str] = ...) -> None: ...
