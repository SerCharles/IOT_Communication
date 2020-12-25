我们的代码运行在src下，首先进入这个目录，输入如下命令安装依赖

```shell
pip install -r requirements.txt
```

之后测试FSK解码，请把excel格式的文件命名为content.csv放在src根目录下，将待解调的文件命名为res.wav放在src/receive文件夹下，输入如下命令来运行解码测试程序，获取准确率和解码结果。

```shell
python FSK.py
```

准确率在命令行显示，解码结果在src根目录下的result.csv下