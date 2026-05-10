import subprocess

from .player_process import PlayerProcess


class DockerProcess(PlayerProcess):
    def __init__(
            self,
            image_name: str,
            memory_limit: str,
            cpu_limit: str,
            container_name: str|None = None
        ) -> None:
        self.image_name = image_name
        self.container_name = container_name or image_name

        self.memory_limit = memory_limit
        self.cpu_limit = cpu_limit

        process_args = ["docker", "start", "-a", "-i", self.container_name]

        super().__init__(process_args)
    

    def start_preparing(self) -> None:
        self._preparing_process: subprocess.Popen = subprocess.Popen(
            [
                "docker", "create",
                "--name", self.container_name,
                "-i",
                "-m", self.memory_limit,
                "--memory-swap", self.memory_limit,  # This prevents using swap
                "--cpus", self.cpu_limit,
                self.image_name
            ],
        )
    
    def join_preparation(self, timeout: float) -> None:
        try:
            self._preparing_process.wait(timeout=timeout)
        except subprocess.TimeoutExpired:
            self._preparing_process.kill()
            self._preparing_process.wait()

            self.cleanup()

            raise TimeoutError(f"Container {self.container_name} preparation timed out")
    
    def cleanup(self, deletion_timeout: float=15.0) -> None:
        super().cleanup()

        try:
            subprocess.run(
                ["docker", "rm", "-f", self.container_name],
                timeout=deletion_timeout,
                stdout=subprocess.DEVNULL,
            )
        except subprocess.TimeoutExpired:
            raise RuntimeError(f"Container memory leak: {self.container_name} was not removed after game end")