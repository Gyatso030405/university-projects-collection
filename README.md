---


---

<h1 id="一些说明">一些说明</h1>
<h2 id="第一部分">第一部分</h2>
<blockquote>
<p>这个项目是我将一些以往的课程项目收集，供学弟学妹们参考学习。由于水平有限，可能存在一些问题或不足之处，望谅解！（本文档由 <a href="https://stackedit.io/">StackEdit</a>.编写。）</p>
</blockquote>
<blockquote>
<p>此项目我将部分项目陆续上传，有遗漏或者有建议可以发我邮箱:gyatso0405@gmail.com，大家也可以在这个仓库里面上传自己的项目，共同完善！<br>
贡献方法：</p>
</blockquote>
<pre><code>-   Fork 本仓库
-   按照已有结构添加自己的项目（建议放在子目录中）
-   提交 Pull Request
</code></pre>
<p>到目前，库里有<em>数据结构作业</em> ；<em>FPGA数字钟</em>  ；<em>单片机小车</em> ；<em>STM32温湿度检测机</em> 等等。<br>
由于该项目会较为庞杂，有些项目可能还暂且不需要下载。所以为了方便下载你所要的项目，<a href="https://minhaskamal.github.io/DownGit/#/home">点击这里</a>,仓库某个<strong>具体文件夹的链接粘贴进去</strong>，比如：</p>
<pre><code>https://github.com/Gyatso030405//raspi-LLM/blob/master/qwen2.5-0.5b-instruct-q2_k.zip
</code></pre>
<p>还有一些其他项目地址：<br>
<a href="https://github.com/Gyatso030405/flash_streaming_video_raspi/tree/master">树莓派网页端视频流</a><br>
<a href="https://github.com/Gyatso030405/Visual-Fourier">基于MATLAB的傅里叶可视化</a><br>
<a href="https://github.com/Gyatso030405/ultrasound_meter_code/tree/master">FPGA(Vivado)超声波测距</a><br>
<a href="https://github.com/Gyatso030405/raspi-LLM">本地LLM驱动的自拍器(树莓派外设控制)</a></p>
<h2 id="第二部分">第二部分</h2>
<blockquote>
<p>这里我就讲一下科学上网（VPN）的一些方法，希望会给大家提供一些帮助。我会在项目库里提供 <code>Clash</code>软件以及推荐一些好用的机场。</p>
</blockquote>
<pre><code> 注意！！！：如果是新手，大家在使用这样更广阔的平台时，一定要有明辨是非的能力，外面的互联网环境各种资料非常丰富(只要英语好)，但也非常危险，各种反动思想无处不在！切记擦亮眼睛！！
</code></pre>
<p>clash软件<a href="">windows/Android/Mac/Linux</a><br>
机场：<br>
<a href="%5B%E8%82%A5%E7%8C%AB%E4%BA%91%E6%9C%BA%E5%9C%BA-%E5%A4%A7%E5%B8%A6%E5%AE%BD%E4%B8%8D%E9%99%90%E9%80%9F%E4%B8%93%E7%BA%BF%E6%9C%BA%E5%9C%BA%5D(https://fccc02.fatcatcloud.me/#/stage/dashboard)">肥猫云</a>(个人使用，比较推荐)<br>
<a href="https://3jkkvi9afjjln2yjwnbc.wgetcloud.org/">WegetCloud</a><br>
大家也可以按自己情况在网上找一些(<a href="https://clashcn.com/">这个网站</a>可能也会帮到大家)，也有一些免费的(但可能不会特别稳定)。如今在网上这种东西很多。对于这番方面有兴趣的也可以自己尝试搭建一些，不过成本会比直接购买一个稳定的<code>商业机场</code>订阅会高一些，需要租国外<code>VPS</code>和<code>域名</code>。</p>
<pre><code>提示：具体使用方法一般每个机场都有教程，我就不都追溯了。
</code></pre>
<p>还有就是<code>IOS</code>系统的科学上网，由于iPhone，iPad的系统环境特点，想要挂梯子会比较困难。下面我讲个大概思路。（我也没试过）</p>
<ol>
<li>一种是直接在AppStore里面变更地区，但这样的话，如果你已经订阅了中国区的 Apple 服务（如 Apple Music、iCloud+、订阅 app），<strong>必须先取消所有订阅并等待过期</strong>才能切换。</li>
</ol>
<ul>
<li>
<p>原来的中国区购买记录可能暂时无法访问。</p>
</li>
<li>
<p>切换频繁可能触发风控。</p>
</li>
</ul>
<ol start="2">
<li>
<p>注册美区<code>Apple ID</code> :首先在<a href="https://account.apple.com/">Apple账户</a>网站注册一个美区苹果账号。这个<a href="https://naiyous.com/7829.html">网站</a>会给你提供帮助，里面的邮箱最好用<code>gmail.com</code>或者<code>outlook.com</code>等国外邮箱，最好不要<code>QQ</code>(并非完全不可用)。里面的电话号码就不要用生成器生成，可以打开地图，随便在地图上找一个当地酒店等的电话号码使用（你以后恐怕也用不上，不必担心，只是为了注册账号）。</p>
</li>
<li>
<p>创建完自己的美区<code>Apple ID</code>后，设备在<code>AppStore</code>登录并找到<code>Shadowrocket</code>，一个有火箭标志的软件(为付费软件)。</p>
</li>
<li>
<p>然后便是付费问题(一般这里是最难的)，一般情况下就是购买<code>礼品卡</code>，由于我们没有国外信用卡，所以相当的不方便，这里给大家推荐一些网站或方法：</p>
<pre><code>注意：这些方法本人没有尝试过，仅供参考！！！
</code></pre>
</li>
</ol>
<p><a href="https://www.seagm.com/zh-cn">SEAGM</a>   (支持支付宝，微信等)<br>
也可以在<code>支付宝</code>里面直接搜<code>礼品卡</code>找到<code>PockyShop</code>进行购买尝试。<br>
其他也有<a href="https://www.amazon.com/">亚马逊</a>；<a href="https://www.mygiftcardsupply.com/">MyGiftCardSupply</a>等网站，但由于支付方式等，可能不会很方便。大概便是如此。</p>
<h2 id="第三部分">第三部分</h2>
<blockquote>
<p>这里的话到目前为止还没想好要写什么，可能以后会补充，大家也可以按自己的生活生活学习经验在这里进行补充。</p>
</blockquote>
<ol>
<li>我本人作为通信专业的学生，没有进行过系统的学习<code>python</code>语言，哪怕做过很多基于此语言的项目，依旧感觉自己对此语言相当的不熟悉。而<code>python</code>语言作为使用最广泛的语言，对其有基本的了解，对我们有非常大的帮助，这里给大家推荐一个学习<code>python</code>的<a href="https://github.com/jackfrued/Python-100-Days">项目</a>，希望给大家的学习带来帮助！！！</li>
</ol>

