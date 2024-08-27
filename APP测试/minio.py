from fastapi import FastAPI, UploadFile, File, HTTPException
from minio import Minio
import asyncio
from concurrent.futures import ThreadPoolExecutor
from functools import partial
import io

app = FastAPI()

# 创建 MinIO 客户端
minio_client = Minio(
    "your-minio-endpoint",
    access_key="your-access-key",
    secret_key="your-secret-key",
    secure=True,  # 如果使用 HTTPS 则设为 True
)

# 创建一个线程池执行器
thread_pool = ThreadPoolExecutor(max_workers=10)  # 调整 max_workers 以适应您的需求


async def async_put_object(
    bucket_name: str, object_name: str, data: bytes, length: int
):
    loop = asyncio.get_running_loop()
    # 使用偏函数来固定某些参数
    func = partial(
        minio_client.put_object, bucket_name, object_name, io.BytesIO(data), length
    )
    # 在线程池中执行同步操作
    await loop.run_in_executor(thread_pool, func)


async def async_get_object(bucket_name: str, object_name: str):
    loop = asyncio.get_running_loop()
    func = partial(minio_client.get_object, bucket_name, object_name)
    # 在线程池中执行同步操作
    response = await loop.run_in_executor(thread_pool, func)
    return await loop.run_in_executor(thread_pool, response.read)


@app.post("/upload/")
async def upload_file(file: UploadFile = File(...)):
    try:
        contents = await file.read()
        await async_put_object(
            "your-bucket-name", file.filename, contents, len(contents)
        )
        return {"message": "File uploaded successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/download/{filename}")
async def download_file(filename: str):
    try:
        data = await async_get_object("your-bucket-name", filename)
        return data
    except Exception as e:
        raise HTTPException(status_code=404, detail="File not found")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
