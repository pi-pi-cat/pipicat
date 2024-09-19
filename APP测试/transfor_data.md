import asyncio
import asyncssh

async def run_remote_command(host, command):
    async with asyncssh.connect(host) as conn:
        result = await conn.run(command)
        return result.stdout

async def main():
    host_b = 'ip_of_machine_b'
    mounted_shared_dir = '/path/to/mounted/shared_folder_on_B'
    destination = '/path/on/machine_b'
    
    # 使用rsync在B机器上从挂载点复制到目标目录
    command = f'rsync -avz "{mounted_shared_dir}" "{destination}"'
    
    result = await run_remote_command(host_b, command)
    print(result)

asyncio.run(main())


async def transfer_file(conn, local_path, remote_path):
    await conn.run(f"mkdir -p {os.path.dirname(remote_path)}")
    async with conn.start_sftp_client() as sftp:
        await sftp.put(local_path, remote_path)
    print(f"Transferred: {local_path} -> {remote_path}")
