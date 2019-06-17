FROM python:3.7
ENV TZ Asia/Shanghai
WORKDIR /usr/src/app
COPY ./requirements.txt .
RUN pip install -i https://pypi.tuna.tsinghua.edu.cn/simple --no-cache-dir -r requirements.txt
COPY . .
WORKDIR /usr/src/app/
CMD [ "python", "main.py" ]