# dalle demo
Generate headshot with single image captured by mobile phones

## Usage

### dall-e 2 demo

1. create virtual environment
```shell
conda create -n headshot python=3.9 -y
conda acivate headshot
pip install -r requirements.txt
```

2. set openai key
> create a .env file in dalle2 directory, fill your key with format "OPENAI_KEY=sk-*****"   

3. launch server 
```shell
cd dalle2
python main.py
```

4. running test

if you test in a terminal, just run

```shell
curl --location 'http://localhost:50001/headshots/gen' \
--form 'file=@"/home/yourtest.jpeg"'
```

you also can test in web browser provided by fastapi, in our case
[fastapi doc](http://localhost:50001/docs), and "try it out".

