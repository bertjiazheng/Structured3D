---
layout: project
urltitle:  "Structured3D Dataset"
title: "Structured3D"
categories: computer vision, computer graphics, robotics, machine learning
permalink: /
---

<br>
<div class="row">
  <div class="col-xs-12">
    <center><h2>Structured3D: A Large Photo-realistic Dataset for Structured 3D Modeling</h2></center>
  </div>
</div>

<hr>

<div class="row">
  <div class="col-md-12">
    <img src="{{ "/static/img/teaser.png" | prepend:site.baseurl }}">
    <p>
      Structured3D is a large-scale photo-realistic dataset containing 3.5K house designs (a) created by professional designers with a variety of ground truth 3D structure annotations (b) and generate photo-realistic 2D images (c).
    </p>
  </div>
</div>

<br>
<div class="row" id="news">
  <div class="col-xs-12">
    <h2>News</h2>
  </div>
</div>

<div class="row">
  <div class="col-xs-12">
    <ul>
      <li>2020-05-22: We are hosting the <a href="https://holistic-3d.github.io/eccv20/challenge.html" target="_blank">Holistic 3D Vision Challenges</a> on the <a href="https://holistic-3d.github.io/eccv20" target="_blank">Holistic Scene Structures for 3D Vision Workshop</a> at <a href="http://eccv2020.eu/" target="_blank">ECCV 2020</a>.</li>
      <li>2019-10-16: The 3D bounding box of each instance is now available!</li>
      <li>2019-09-11: The perspective part of the Structured3D dataset is now available!</li>
      <li>2019-08-01: Structured3D dataset (panoramic images) and basic code for visualization are now available!</li>
    </ul>
  </div>
</div><br>

<div class="row" id="abstract">
  <div class="col-xs-12">
    <h2>Abstract</h2>
  </div>
</div>

<div class="row">
  <div class="col-xs-12">
    <p>
      Recently, there has been growing interest in developing learning-based methods to detect and utilize salient semi-global or global structures, such as junctions, lines, planes, cuboids, smooth surfaces, and all types of symmetries, for 3D scene modeling and understanding. However, the ground truth annotations are often obtained via human labor, which is particularly challenging and inefficient for such tasks due to the large number of 3D structure instances (<em>e.g.</em>, line segments) and other factors such as viewpoints and occlusions. In this paper, we present a new synthetic dataset, Structured3D, with the aim to providing large-scale photo-realistic images with rich 3D structure annotations for a wide spectrum of structured 3D modeling tasks. We take advantage of the availability of millions of professional interior designs and automatically extract 3D structures from them. We generate high-quality images with an industry-leading rendering engine. We use our synthetic dataset in combination with real images to train deep networks for room layout estimation and demonstrate improved performance on benchmark datasets.
    </p>
  </div>
</div><br>

<div class="row" id="paper">
  <div class="col-xs-12">
    <h2>Paper</h2>
  </div>
</div>

<div class="row">
  <div class="col-xs-12" style="margin-top: 3px; color: #666;">
    <b>Structured3D: A Large Photo-realistic Dataset for Structured 3D Modeling</b><br>
    Jia Zheng*, Junfei Zhang*, Jing Li, Rui Tang, Shenghua Gao, Zihan Zhou<br>
    arXiv preprint 2019 /
    <a href="https://arxiv.org/abs/1908.00222">Preprint</a> /
    <a href="https://drive.google.com/file/d/17F_jIfY_QKFNmsOSvzUFZwWKrr6YUMnQ">Supplementary Material</a> /
    <a href="https://github.com/bertjiazheng/Structured3D">Code</a> <br>
    <span style="font-size:15px;">* Equal contribution</span>
  </div>
</div><br>

<div class="row" id="download">
  <div class="col-xs-12">
    <h2>Download</h2>
  </div>
</div>

<div class="row">
  <div class="col-xs-12">
    <p>
      To download the dataset, please fill the <a href="https://forms.gle/LXg4bcjC2aEjrL9o8">agreement form</a> that indicate you agree to the <a href="https://drive.google.com/open?id=13ZwWpU_557ZQccwOUJ8H5lvXD7MeZFMa">Structured3D Terms of Use</a>. After we receive your agreement form, we will provide download access to the dataset. We also provide the <a href="https://github.com/bertjiazheng/Structured3D">basic code</a> for for viewing the structure annotations of our dataset.
    </p>
  </div>
</div><br>

<div class="row" id="license">
  <div class="col-xs-12">
    <h2>License</h2>
  </div>
</div>

<div class="row">
  <div class="col-xs-12">
    <p>
      The data is released under the <a href="https://drive.google.com/open?id=13ZwWpU_557ZQccwOUJ8H5lvXD7MeZFMa">Structured3D Terms of Use</a>, and the <a href="https://github.com/bertjiazheng/Structured3D">code</a> is released under the MIT license.
    </p>
  </div>
</div><br>

<div class="row" id="people">
  <div class="col-xs-12">
    <h2>People</h2>
  </div>
</div>

<div class="row">
  <div class="col-md-2 col-sm-3 col-xs-6">
    <a href="https://bertjiazheng.github.io/">
      <img class="people-pic" src="{{ "/static/img/people/jia.jpg" | prepend:site.baseurl }}">
    </a>
    <div class="people-name">
      <a href="https://bertjiazheng.github.io/">
        Jia Zheng
      </a>
      <h6>ShanghaiTech University</h6>
    </div>
  </div>

  <div class="col-md-2 col-sm-3 col-xs-6">
    <a href="https://www.linkedin.com/in/骏飞-张-1bb82691/?locale=en_US">
      <img class="people-pic" src="{{ "/static/img/people/ahui.png" | prepend:site.baseurl }}">
    </a>
    <div class="people-name">
      <a href="https://www.linkedin.com/in/骏飞-张-1bb82691/?locale=en_US">
        Junfei Zhang
      </a>
      <h6>Kujiale.com</h6>
    </div>
  </div>

  <div class="col-md-2 col-sm-3 col-xs-6">
    <a href="https://www.linkedin.com/in/jing-li-253b26139/?originalSubdomain=cn">
      <img class="people-pic" src="{{ "/static/img/people/jing.jpg" | prepend:site.baseurl }}">
    </a>
    <div class="people-name">
      <a href="https://www.linkedin.com/in/jing-li-253b26139/?originalSubdomain=cn">
        Jing Li
      </a>
      <h6>ShanghaiTech University</h6>
    </div>
  </div>

  <div class="col-md-2 col-sm-3 col-xs-6">
    <a href="https://cn.linkedin.com/in/rui-tang-50973488">
      <img class="people-pic" src="{{ "/static/img/people/ati.jpg" | prepend:site.baseurl }}">
    </a>
    <div class="people-name">
      <a href="https://cn.linkedin.com/in/rui-tang-50973488">
        Rui Tang
      </a>
      <h6>Kujiale.com</h6>
    </div>
  </div>

  <div class="col-md-2 col-sm-3 col-xs-6">
    <a href="http://sist.shanghaitech.edu.cn/sist_en/2018/0820/c3846a31775/page.htm">
      <img class="people-pic" src="{{ "/static/img/people/shenghua.jpg" | prepend:site.baseurl }}">
    </a>
    <div class="people-name">
      <a href="http://sist.shanghaitech.edu.cn/sist_en/2018/0820/c3846a31775/page.htm">Shenghua Gao</a>
      <h6>ShanghaiTech University</h6>
    </div>
  </div>

  <div class="col-md-2 col-sm-3 col-xs-6">
    <a href="https://faculty.ist.psu.edu/zzhou/">
      <img class="people-pic" src="{{ "/static/img/people/zihan.jpg" | prepend:site.baseurl }}">
    </a>
    <div class="people-name">
      <a href="https://faculty.ist.psu.edu/zzhou/">Zihan Zhou</a>
      <h6>Penn State University</h6>
    </div>
  </div>
</div><br>

<div class="row">
  <div class="col-xs-12">
    <h2>Acknowledgements</h2>
  </div>
</div>

<div class="row">
  <div class="col-xs-12">
    <p>
      We would like to thank <a href="https://Kujiale.com">Kujiale.com</a> for providing the database of house designs and the rendering engine.
    </p>
  </div>
</div><br>

<hr>
