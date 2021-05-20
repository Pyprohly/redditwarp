
class IResumable:
    def resume(self) -> None:
        raise NotImplementedError

class IResettable:
    def reset(self) -> None:
        raise NotImplementedError
