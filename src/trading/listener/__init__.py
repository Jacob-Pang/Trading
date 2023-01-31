import time

from threading import Thread, Semaphore
from pyutils.events import wait_for

class ListenerBase:
    _update_semaphore: Semaphore = Semaphore(1)
    _update_loop_thread: Thread = None
    _active_update_loop: bool = False

    def update_loop_inactive(self) -> bool:
        return not self._active_update_loop

    # Initializers
    def subscribe(self) -> None:
        # Subscribe to the connection
        pass

    def ready(self) -> bool:
        # Returns whether the connection is ready
        return True

    # Getter
    def get(self) -> any:
        raise NotImplementedError()

    # Mutator
    def update(self) -> None:
        # Derived methods should utilize self._update_semaphore
        raise NotImplementedError()

    # Destructors
    def close(self) -> None:
        # Closes the connection
        self.stop_update_loop()
        assert wait_for(self.update_loop_inactive, timeout=10)

    # Events
    def run_update_loop(self, update_freq: float = .5, resubscription_rate: float = None,
        subscription_timeout: int = 10) -> None:
        
        def _run_update_loop(listener: ListenerBase, update_freq: float,
            resubscription_rate: float, subscription_timeout: int) -> None:

            next_loop_timestamp = 0
            resubscription_timestamp = time.time() + resubscription_rate \
                    if resubscription_rate else None

            while not listener.update_loop_inactive():
                time.sleep(max(next_loop_timestamp - time.time(), 0))
                loop_timestamp = time.time()
                
                if resubscription_rate and loop_timestamp > resubscription_timestamp:
                    listener.subscribe()
                    assert wait_for(listener.ready, timeout=subscription_timeout)

                    resubscription_timestamp += resubscription_rate

                listener.update()
                next_loop_timestamp = loop_timestamp + update_freq

        assert self.update_loop_inactive()
        self._active_update_loop = True
        self._update_loop_thread = Thread(target=_run_update_loop, args=(self, update_freq,
                resubscription_rate, subscription_timeout)).start()

    def stop_update_loop(self) -> None:
        self._active_update_loop = False

if __name__ == "__main__":
    pass