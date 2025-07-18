---


---

<h1 id="无线通信系统实践">无线通信系统实践</h1>
<p><img src="https://github.com/Gyatso030405/university-projects-collection/blob/master/%E6%97%A0%E7%BA%BF%E9%80%9A%E4%BF%A1%E7%B3%BB%E7%BB%9F%E5%AE%9E%E8%B7%B5%E5%AE%9E%E9%AA%8C/files/images/1.jpg" alt=""></p>
<blockquote>
<p>This article was written with <a href="https://stackedit.io/">StackEdit</a>.</p>
</blockquote>
<h2 id="环境配置">环境配置</h2>
<h3 id="windows版">Windows版</h3>
<blockquote>
<p>首先是环境配置问题，我会将我的原有的虚拟环境一并上传，可以尝试直接使用（不推荐）。自己搭建的方法和<code>conda</code>虚拟环境的配置文件<code>environment.yml</code>一并上传。</p>
</blockquote>
<p>对于PlutoSDR的环境配置，可以按照这个<a href="https://github.com/Gyatso030405/university-projects-collection/blob/master/%E6%97%A0%E7%BA%BF%E9%80%9A%E4%BF%A1%E7%B3%BB%E7%BB%9F%E5%AE%9E%E8%B7%B5%E5%AE%9E%E9%AA%8C/files/Lab0%20%E9%85%8D%E7%BD%AEPluto%E7%8E%AF%E5%A2%83.pdf">PDF1</a>和这个<a href="https://github.com/Gyatso030405/university-projects-collection/blob/master/%E6%97%A0%E7%BA%BF%E9%80%9A%E4%BF%A1%E7%B3%BB%E7%BB%9F%E5%AE%9E%E8%B7%B5%E5%AE%9E%E9%AA%8C/files/%E4%B8%80%E3%80%81Lab0%20%E9%85%8D%E7%BD%AEPluto%E7%8E%AF%E5%A2%83%EF%BC%88V1.1%EF%BC%89.pdf">PDF2</a>文件，大致步骤如下：</p>
<ol>
<li>
<p>下载并安装 PlutoSDR-M2k-USB-Drivers-v0.8<br>
下载地址：<br>
<a href="https://github.com/analogdevicesinc/plutosdr-m2k-drivers-win/releases/download/v0.8/PlutoSDR-M2k-USB-Drivers.exe">https://github.com/analogdevicesinc/plutosdr-m2k-drivers-win/releases/download/v0.8/PlutoSDR-M2k-USB-Drivers.exe</a></p>
</li>
<li>
<p>下载并安装 libiio-0.23.gc14a0f8-Windows-setup<br>
下载地址：<br>
<a href="https://github.com/analogdevicesinc/libiio/releases/download/v0.23/libiio-0.23.gc14a0f8-Windows-setup.exe">https://github.com/analogdevicesinc/libiio/releases/download/v0.23/libiio-0.23.gc14a0f8-Windows-setup.exe</a></p>
</li>
<li>
<p>下载并安装miniconda (主要用于管理Python环境，也可用conda)</p>
</li>
</ol>
<blockquote>
<p>如果你的电脑里本来就有<code>Anaconda</code>，这里就不用下载了。如果没有就下载<code>miniconda</code>要不然Anaconda太大了，你也可能用不上那么多功能，徒占电脑内存。可以直接在浏览器搜<code>miniconda</code>或者用下面课程给的清华镜像源网址：</p>
</blockquote>
<p><a href="https://mirrors.tuna.tsinghua.edu.cn/anaconda/miniconda/Miniconda3-py37_4.9.2-Windows-x86_64.exe">https://mirrors.tuna.tsinghua.edu.cn/anaconda/miniconda/Miniconda3-py37_4.9.2-Windows-x86_64.exe</a></p>
<pre><code>注意！！本次实验当中，使用`conda`虚拟环境时，python版本要在py37~py39;要不然可能会报错！
</code></pre>
<ol start="4">
<li>安装必要python packages</li>
</ol>
<blockquote>
<p>这里就是用<code>conda</code>创建虚拟环境，作为你的实验环境，安装各种包和代码的运行。我会将我所安装的所有库的目录文件<code>environment.yml</code>放在Lab1目录下,用以大家更加方便的部署，也会给出自己创建方法。</p>
</blockquote>
<ul>
<li>首先讲一下我给的环境配置文件，将实验内容<a href="https://minhaskamal.github.io/DownGit/#/home">下载</a>，在Pycharm或者VSCode(看你自己用什么IDE)终端进入Lab1的（<code>environment.yml</code>文件所在目录），输入如下命令即可（可以重建我做的虚拟化就<code>pluto_env</code>）：</li>
</ul>
<pre><code>    #创建并激活新环境
    conda env create -f environment.yml
    conda activate pluto_env
</code></pre>
<ul>
<li>接下来就是自己搭建虚拟环境的大致流程：</li>
</ul>
<pre><code>    conda activate base      #创建虚拟环境 base
    pip install pylibiio==0.23.1
    pip install pyadi-iio==0.0.12
    pip install scipy==1.7.3 numpy==1.21.4
</code></pre>
<p>还要下载<code>matplotlib</code>用以图像显示，推荐<code>matplotlib==3.5.1</code>版本，可以用命令<code>conda install matplotlib</code>来下载，他会自动选择合适的版本，也可以用如下的命令卸载原本不兼容的版本，下载指定版本：<br>
<code>pip uninstall matplotlib</code><br>
<code>pip install matplotlib==3.5.1</code></p>
<blockquote>
<p>用<code>pip</code>命令会从你的设备默认源地址下载，一般情况下时官方源，也有可能你自己之前设置过镜像源，如清华源、阿里源等。</p>
</blockquote>
<blockquote>
<p>如果你的默认源有问题，可以在下载时自定义下载源，比如从官方源下载：<br>
<code>pip install matplotlib==3.5.1 -i https://pypi.org/simple</code><br>
清华源、阿里源等也可以自己定义。</p>
</blockquote>
<ol start="5">
<li>插入Pluto硬件，并进行测试</li>
</ol>
<pre><code>    $ conda activate base   或者   conda activate pluto_env
    $ python
    &gt;&gt;&gt; import adi
    &gt;&gt;&gt; sdr = adi.Pluto('ip:192.168.3.1') # 这里要注意用自己的Pluto IP
    &gt;&gt;&gt; sdr.sample_rate = int(2.5e6)
    &gt;&gt;&gt; sdr.rx()
    
</code></pre>
<blockquote>
<p>关于查找自己<code>Pluto IP</code>的方法，会在这个<a href="https://github.com/Gyatso030405/university-projects-collection/blob/master/%E6%97%A0%E7%BA%BF%E9%80%9A%E4%BF%A1%E7%B3%BB%E7%BB%9F%E5%AE%9E%E8%B7%B5%E5%AE%9E%E9%AA%8C/files/%E5%AE%9E%E9%AA%8C%E4%B8%80_%E7%AC%AC%E4%B8%89%E9%83%A8%E5%88%86_%E6%94%B6%E5%8F%91%E8%AE%BE%E5%A4%87%E8%BF%9E%E6%8E%A5%E6%96%B9%E6%B3%95.pdf">PDF</a>文件里！</p>
</blockquote>
<p>Pluto连接成功可以发送图片，会显示如下：</p>
<p>至此PLuto配置已算是完成了，可以做实验了！</p>
<h3 id="linux版">Linux版</h3>
<blockquote>
<p>Linux的配置环境办法在该<a href="">PDF</a>里面，可以尝试。可以用<code>WSL</code>的<code>Ubuntu</code></p>
</blockquote>
<h2 id="lab1-帧同步实验">Lab1 帧同步实验</h2>
<blockquote>
<p>Lab1实验的源码和实验报告我都会一同上传！</p>
</blockquote>
<p><a href="https://github.com/Gyatso030405/university-projects-collection/blob/master/%E6%97%A0%E7%BA%BF%E9%80%9A%E4%BF%A1%E7%B3%BB%E7%BB%9F%E5%AE%9E%E8%B7%B5%E5%AE%9E%E9%AA%8C/files/%E6%97%A0%E7%BA%BF%E9%80%9A%E4%BF%A1%E7%B3%BB%E7%BB%9F%E5%AE%9E%E8%B7%B5Lab1.docx">实验报告</a>在这里，可以下载，<code>github</code>不支持在线阅读<code>.docx</code>文件，可以下载在阅读，下载实验一<a href="https://github.com/Gyatso030405/university-projects-collection/tree/master/%E6%97%A0%E7%BA%BF%E9%80%9A%E4%BF%A1%E7%B3%BB%E7%BB%9F%E5%AE%9E%E8%B7%B5%E5%AE%9E%E9%AA%8C/Lab1">Lab1</a>以及<a href="https://github.com/Gyatso030405/university-projects-collection/blob/master/%E6%97%A0%E7%BA%BF%E9%80%9A%E4%BF%A1%E7%B3%BB%E7%BB%9F%E5%AE%9E%E8%B7%B5%E5%AE%9E%E9%AA%8C/files/%E6%97%A0%E7%BA%BF%E9%80%9A%E4%BF%A1%E7%B3%BB%E7%BB%9F%E5%AE%9E%E8%B7%B5Lab1.docx">实验报告一</a></p>
<h2 id="labe2-物理层实验">Labe2 物理层实验</h2>
<blockquote>
<p>Lab2实验的源码和实验报告我都会一同上传！</p>
</blockquote>
<p>实验二的<a href="https://github.com/Gyatso030405/university-projects-collection/tree/master/%E6%97%A0%E7%BA%BF%E9%80%9A%E4%BF%A1%E7%B3%BB%E7%BB%9F%E5%AE%9E%E8%B7%B5%E5%AE%9E%E9%AA%8C/Lab2">实验文件</a>以及<a href="https://github.com/Gyatso030405/university-projects-collection/blob/master/%E6%97%A0%E7%BA%BF%E9%80%9A%E4%BF%A1%E7%B3%BB%E7%BB%9F%E5%AE%9E%E8%B7%B5%E5%AE%9E%E9%AA%8C/files/%E6%97%A0%E7%BA%BF%E9%80%9A%E4%BF%A1%E7%B3%BB%E7%BB%9F%E5%AE%9E%E9%AA%8CLab2.docx">报告</a>，不过我个人认为由于老师在实验作业所给的文件有些问题，因此实验二当中代码所绘制出来的图像都有些问题，比如明明是<code>BPSK</code>解调绘制的星座图，却像<code>QPSK</code>解调结果，因此可以参考这个<a href="https://github.com/Gyatso030405/university-projects-collection/tree/master/%E6%97%A0%E7%BA%BF%E9%80%9A%E4%BF%A1%E7%B3%BB%E7%BB%9F%E5%AE%9E%E8%B7%B5%E5%AE%9E%E9%AA%8C/Lab2__ReferenceVersion">参考版本文件</a>里的代码，这里面的代码虽然可能跟实验要求有小出入，但是实验结果更加符合我们的要求。</p>
<h2 id="project-大作业">Project 大作业</h2>
<blockquote>
<p>最后是大作业，源码与报告一同上传！</p>
</blockquote>
<p>大作业<a href="https://github.com/Gyatso030405/university-projects-collection/tree/master/%E6%97%A0%E7%BA%BF%E9%80%9A%E4%BF%A1%E7%B3%BB%E7%BB%9F%E5%AE%9E%E8%B7%B5%E5%AE%9E%E9%AA%8C/Project">源码</a>以及<a href="https://github.com/Gyatso030405/university-projects-collection/blob/master/%E6%97%A0%E7%BA%BF%E9%80%9A%E4%BF%A1%E7%B3%BB%E7%BB%9F%E5%AE%9E%E8%B7%B5%E5%AE%9E%E9%AA%8C/files/%E6%97%A0%E7%BA%BF%E9%80%9A%E4%BF%A1%E7%B3%BB%E7%BB%9F%E5%AE%9E%E8%B7%B5_%E5%A4%A7%E4%BD%9C%E4%B8%9A.docx">实验报告</a>，由于假期近在眼前，鄙人并没能有足够的时间把该大作业做完整！望见谅！（哈哈哈！）总之，具体情况看源码和实验报告！</p>

