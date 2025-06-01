import docker
from docker.errors import APIError
from typing import Optional
from datetime import datetime


class DockerDatasource:
    def __init__(self) -> None:
        self.client = docker.from_env()

    def list_containers(self, search: str = "") -> list:
        containers = self.client.containers.list(all=True)
        result = []
        for c in containers:
            try:
                networks = list(c.attrs["NetworkSettings"]["Networks"].keys())
            except KeyError:
                networks = []
            try:
                volumes_list = []
                mounts = c.attrs.get("Mounts", [])
                for m in mounts:
                    # если том именованный, m["Name"], иначе — путь назначения
                    volumes_list.append(m.get("Name") or m.get("Destination") or "")
            except KeyError:
                volumes_list = []
            result.append(
                {
                    "id": c.id,
                    "name": c.name,
                    "status": c.status,
                    "image": c.image.tags[0] if c.image.tags else "",
                    "networks": ", ".join(networks),
                    "volumes": volumes_list,
                }
            )
        return [r for r in result if search.lower() in r["name"].lower()]

    def remove_container(self, container_id: str) -> str:
        container = self.client.containers.get(container_id=container_id)
        container.remove(force=True)
        return container_id

    def start_container(self, container_id: str) -> None:
        container = self.client.containers.get(container_id=container_id)
        if container.status != "running":
            container.start()

    def stop_container(self, container_id: str) -> None:
        container = self.client.containers.get(container_id=container_id)
        if container.status == "running":
            container.stop()

    def get_logs(
        self,
        container_id: str,
        since: Optional[int] = None,
        until: Optional[int] = None,
    ) -> str:
        container = self.client.containers.get(container_id=container_id)
        kwargs = {"stdout": True, "stderr": True, "timestamps": False}
        if since is not None:
            kwargs["since"] = since
        if until is not None:
            kwargs["until"] = until
        try:
            logs_bytes = container.logs(**kwargs)
            if isinstance(logs_bytes, bytes):
                return logs_bytes.decode(errors="ignore")
            else:
                # Если возвращается генератор
                decoded = b"".join(logs_bytes)
                return decoded.decode(errors="ignore")
        except APIError as e:
            raise

    def exec_command(self, container_id: str, cmd: str) -> str:
        container = self.client.containers.get(container_id=container_id)
        result = container.exec_run(cmd)
        return result.output.decode(errors="ignore")

    def list_images(self) -> list:
        images = self.client.images.list()
        result = []
        for img in images:
            # У многих образов может быть несколько тегов, возьмём первый или id
            tag = img.tags[0] if img.tags else img.id
            result.append({"id": img.id, "repo_tag": tag, "created": datetime.fromtimestamp(img.attrs["Created"])})
        return result

    def remove_image(self, image_id: str) -> None:
        # force=True — удаляет, даже если контейнеры всё ещё используют этот образ
        self.client.images.remove(image=image_id, force=True)

    # 1.1.2. Networks
    def list_networks(self) -> list:
        networks = self.client.networks.list()
        result = []
        for net in networks:
            result.append(
                {
                    "id": net.id,
                    "name": net.name,
                    "driver": net.attrs.get("Driver", ""),
                    "containers": net.attrs.get("Containers", {}),  # словарь подключённых контейнеров
                }
            )
        return result

    def remove_network(self, network_id: str) -> None:
        net = self.client.networks.get(network_id)
        net.remove()

    def get_containers_by_network(self, network_id: str) -> list:
        """
        Возвращает массив объектов вида {'id': ..., 'name': ...}
        для тех контейнеров, которые подключены к данной сети.
        """
        net = self.client.networks.get(network_id)
        containers_info = []
        conts = net.attrs.get("Containers", {})  # { <ctr_id>: { ... } }
        for cid, meta in conts.items():
            try:
                c = self.client.containers.get(cid)
                containers_info.append({"id": c.id, "name": c.name, "status": c.status})
            except docker.errors.NotFound:
                continue
        return containers_info

    # ---------------------------
    # Список образов
    # ---------------------------
    def list_images(self) -> list:
        images = self.client.images.list()
        result = []
        for img in images:
            # У многих образов может быть несколько тегов, возьмём первый или id
            tag = img.tags[0] if img.tags else img.id
            # img.attrs["Created"] – это UNIX-время в секундах (или ISO-строка),
            # преобразуем в datetime
            created_ts = img.attrs.get("Created")
            try:
                # Если Created — строка ISO, то datetime.fromisoformat
                created_dt = (
                    datetime.fromisoformat(created_ts)
                    if isinstance(created_ts, str)
                    else datetime.fromtimestamp(created_ts)
                )
            except Exception:
                # на всякий случай fallback в текущее время
                created_dt = datetime.now()

            result.append(
                {"id": img.id, "repo_tag": tag, "created": created_dt.isoformat()}  # передадим ISO-строку на фронт
            )
        return result

    def remove_image(self, image_id: str) -> None:
        self.client.images.remove(image=image_id, force=True)

    # ---------------------------
    # Сети
    # ---------------------------
    def list_networks(self) -> list:
        networks = self.client.networks.list()
        result = []
        for net in networks:
            result.append(
                {
                    "id": net.id,
                    "name": net.name,
                    "driver": net.attrs.get("Driver", ""),
                    "containers": net.attrs.get("Containers", {}),
                }
            )
        return result

    def remove_network(self, network_id: str) -> None:
        net = self.client.networks.get(network_id)
        net.remove()

    def get_containers_by_network(self, network_id: str) -> list:
        net = self.client.networks.get(network_id)
        containers_info = []
        conts = net.attrs.get("Containers", {})
        for cid, meta in conts.items():
            try:
                c = self.client.containers.get(cid)
                containers_info.append({"id": c.id, "name": c.name, "status": c.status})
            except docker.errors.NotFound:
                continue
        return containers_info

    # ---------------------------
    # Томa
    # ---------------------------
    def list_volumes(self) -> list:
        vols = self.client.volumes.list()
        result = []
        for v in vols:
            result.append(
                {
                    "name": v.name,
                    "created_at": v.attrs.get("CreatedAt", ""),
                    "mountpoint": v.attrs.get("Mountpoint", ""),
                    "scope": v.attrs.get("Scope", ""),
                }
            )
        return result

    def remove_volume(self, volume_name: str) -> None:
        vol = self.client.volumes.get(volume_name)
        vol.remove(force=True)


docker_datasource = DockerDatasource()
