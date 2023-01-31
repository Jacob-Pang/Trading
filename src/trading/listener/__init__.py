import time

from threading import Thread, Semaphore
from pyutils.events import wait_for

class ListenerBase:
    _update_semaphore: Semaphore = Semaphore(1)
    _update_loop_thread: Thread = None
    _active_update_loop: bool = False

    def update_loop_inactive(self) -> bool:
        # Returns whether there is an active update loop
        if self._update_loop_thread:
            return not self._update_loop_thread.is_alive()

        return True

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

    # Events
    def run_update_loop(self, update_freq: float = .5, resubscription_rate: float = None,
        subscription_timeout: int = 10) -> None:
        
        def _run_update_loop(listener: ListenerBase, update_freq: float,
            resubscription_rate: float, subscription_timeout: int) -> None:

            next_loop_timestamp = 0
            resubscription_timestamp = time.time() + resubscription_rate \
                    if resubscription_rate else None

            while listener._active_update_loop:
                time.sleep(max(next_loop_timestamp - time.time(), 0))
                loop_timestamp = time.time()
                
                if resubscription_timestamp and loop_timestamp > resubscription_timestamp:
                    listener.subscribe()
                    assert wait_for(listener.ready, timeout=subscription_timeout)

                    resubscription_timestamp = resubscription_timestamp + resubscription_rate \
                            if resubscription_rate else None
                try:
                    listener.update()
                    next_loop_timestamp = loop_timestamp + update_freq
                except: # Forced resubscription
                    resubscription_timestamp = next_loop_timestamp

        assert self.update_loop_inactive()
        self._active_update_loop = True
        self._update_loop_thread = Thread(target=_run_update_loop, args=(self, update_freq,
                resubscription_rate, subscription_timeout)).start()

    def stop_update_loop(self) -> None:
        # Blocking stop
        self._active_update_loop = False
        self._update_loop_thread.join()
        self._update_loop_thread = None # Reset state

if __name__ == "__main__":
    pass