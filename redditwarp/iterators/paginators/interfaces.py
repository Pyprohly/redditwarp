
class IResumable:
    resuming: bool

    def resume(self) -> None:
        self.resuming = True

class IResettable:
    def reset(self) -> None:
        raise NotImplementedError
