# jenkins-update-center  

![GitHub](https://img.shields.io/github/license/lework/jenkins-update-center)
[![](https://data.jsdelivr.com/v1/package/gh/lework/jenkins-update-center/badge)](https://www.jsdelivr.com/package/gh/lework/jenkins-update-center)

Jenkins mirror update center generator


## Update time

Updated daily at 1 AM UTC



## Mirror site

- tencent https://mirrors.cloud.tencent.com/jenkins/
- huawei https://mirrors.huaweicloud.com/jenkins/
- tsinghua https://mirrors.tuna.tsinghua.edu.cn/jenkins/
- ustc https://mirrors.ustc.edu.cn/jenkins/
- bit https://mirrors.bit.edu.cn/jenkins/
- aliyun https://mirrors.aliyun.com/jenkins/



**file update-center.json** 

| Site     | Source                                                       | CDN                                                          |
| -------- | ------------------------------------------------------------ | ------------------------------------------------------------ |
| tencent  | https://raw.githubusercontent.com/lework/jenkins-update-center/master/updates/tencent/update-center.json | https://cdn.jsdelivr.net/gh/lework/jenkins-update-center/updates/tencent/update-center.json |
| huawei   | https://raw.githubusercontent.com/lework/jenkins-update-center/master/updates/huawei/update-center.json | https://cdn.jsdelivr.net/gh/lework/jenkins-update-center/updates/huawei/update-center.json |
| tsinghua | https://raw.githubusercontent.com/lework/jenkins-update-center/master/updates/tsinghua/update-center.json | https://cdn.jsdelivr.net/gh/lework/jenkins-update-center/updates/tsinghua/update-center.json |
| ustc     | https://raw.githubusercontent.com/lework/jenkins-update-center/master/updates/ustc/update-center.json | https://cdn.jsdelivr.net/gh/lework/jenkins-update-center/updates/ustc/update-center.json |
| bit      | https://raw.githubusercontent.com/lework/jenkins-update-center/master/updates/bit/update-center.json | https://cdn.jsdelivr.net/gh/lework/jenkins-update-center/updates/bit/update-center.json |
| aliyun      | https://raw.githubusercontent.com/lework/jenkins-update-center/master/updates/aliyun/update-center.json | https://cdn.jsdelivr.net/gh/lework/jenkins-update-center/updates/aliyun/update-center.json |

**mirror site speed test** 

```bash
curl -sSL https://cdn.jsdelivr.net/gh/lework/jenkins-update-center/speed-test.sh | bash
```



## Usage mirror site

1. Upload custom CA file.

    ```bash
    [ ! -d /var/lib/jenkins/update-center-rootCAs ] && mkdir /var/lib/jenkins/update-center-rootCAs
    wget https://cdn.jsdelivr.net/gh/lework/jenkins-update-center/rootCA/update-center.crt -O /var/lib/jenkins/update-center-rootCAs/update-center.crt
    chown jenkins.jenkins -R /var/lib/jenkins/update-center-rootCAs
    ```

    > Or turn off the signature verification of the update service.
    >
    > ```bash
    > sed -i 's#$JENKINS_JAVA_OPTIONS#$JENKINS_JAVA_OPTIONS -Dhudson.model.DownloadService.noSignatureCheck=true#g' /etc/init.d/jenkins
    > 
    > systemctl daemon-reload
    > ```

2. Change Update Site url.

   ```bash
   sed -i 's#https://updates.jenkins.io/update-center.json#https://cdn.jsdelivr.net/gh/lework/jenkins-update-center/updates/tsinghua/update-center.json#' /var/lib/jenkins/hudson.model.UpdateCenter.xml
   rm -f /var/lib/jenkins/updates/default.json

   systemctl restart jenkins
   ```
   
   > Or it can be modified on the web.
   >
   > Go to `Jenkins` → `Manage Jenkins` → `Manage Plugins` → `Advanced` → Update Site and submit URL to your `https://cdn.jsdelivr.net/gh/lework/jenkins-update-center/updates/tsinghua/update-center.json`



## Steps to create local mirror of Jenkins update center:

1. Clone code:

```bash
git clone https://github.com/lework/jenkins-update-center.git 
```

2. Generate self-signed certificate:

```bash
cd jenkins-update-center
openssl genrsa -out rootCA/update-center.key 2048
openssl req -new -x509 -days 3650 -key rootCA/update-center.key -out rootCA/update-center.crt
```

3. Rsync into your www root directory:

```bash
rsync -avz --delete rsync://rsync.osuosl.org/jenkins/ /var/www/jenkins
```

4. Install dependencies:

```bash
yum -y install make gcc automake autoconf python3-devel git
pip install -r requirements.txt
```
5. Setup mirrors json:

   > Set your mirror url
   
   ```
   # mirrors.json
   {
       "localhost": "http://localhost/jenkins/"
   }
   ```
   
6. Run the following python code:

```bash
python3 generator.py
cp localhost/update-center.json /var/www/jenkins/
```

1. Put `update-center.crt` into `${JENKINS_HOME}/update-center-rootCAs` folder.
2. Go to `Jenkins → Manage Jenkins → Manage Plugins → Advanced → Update Site` and submit URL to your `update-center.json`.

