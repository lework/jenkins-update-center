#!/usr/bin/env python
# -*- coding: utf-8 -*-
# 
# Desc: Jenkins update center generator
# depend:  
#   yum -y install make gcc automake autoconf python3-devel
#   pip install pycrypto


import os
import json
import base64
import binascii
import http.client
import urllib.request
from Crypto.Hash import SHA512, SHA
from Crypto.PublicKey import RSA
from Crypto.Signature import PKCS1_v1_5


class JenkinsUpdateCenter:
  def __init__(self):
    self.updateCenterVersion = "1"
    self.core = None
    self.warnings = None
    self.plugins = None
    self.id = "default"
    self.connectionCheckUrl = None
    self._private_key = None
    self._cert = [None]

  def _sha1_digest(self, body):
    digest = base64.b64encode(SHA.new(body).digest()).decode("utf-8")
    return digest

  def _sha512_digest(self, body):
    digest = binascii.hexlify(SHA512.new(body).digest()).decode("utf-8")
    return digest

  def _sign(self, body, algo = "SHA-1"):
    signer = PKCS1_v1_5.new(self._private_key)
    
    if algo == "SHA-1":
      digest = SHA.new()
    else:
      digest = SHA512.new()

    digest.update(body)

    try:
      signature = signer.sign(digest)
    except Exception as err:
      raise Exception("Could not make sign. "+str(err))
    return signature
    
  def _sha1_signature(self, body):
    signature = base64.b64encode(self._sign(body, "SHA-1")).decode("utf-8")
    return signature

  def _sha512_signature(self, body):
    signature = binascii.hexlify(self._sign(body, "SHA-512")).decode("utf-8")
    return signature

  def load_private(self, key_path):
    try:
      with open(key_path, "r") as fd:
        self._private_key = RSA.importKey(fd.read())
    except Exception as err:
      raise Exception("Could not load private key "+key_path+". "+str(err))

  def load_public(self, key_path):
    try:
      with open(key_path, "rb") as fd:
        self._cert = base64.b64encode(fd.read()).decode("utf-8")
    except Exception as err:
      raise Exception("Could not load public key "+key_path+". "+str(err))

  def out(self, fd):
    output = {}
    output["updateCenterVersion"] = self.updateCenterVersion
    if self.core is not None:
      output["core"] = self.core
    if self.warnings is not None:
      output["warnings"] = self.warnings
    if self.plugins is not None:
      output["plugins"] = self.plugins
    output["id"] = self.id
    if self.connectionCheckUrl is not None:
      output["connectionCheckUrl"] = self.connectionCheckUrl

    payload = (json.dumps(output, separators=(",", ":"), sort_keys=True, ensure_ascii=False).encode("utf-8"))
    output["signature"] = {"certificates":[self._cert]}
    output["signature"]["correct_digest"] = self._sha1_digest(payload)
    output["signature"]["correct_digest512"] = self._sha512_digest(payload)
    output["signature"]["correct_signature"] = self._sha1_signature(payload)
    output["signature"]["correct_signature512"] = self._sha512_signature(payload)

    try:
      fd.write("updateCenter.post(\n"+json.dumps(output, separators=(",", ":"), sort_keys=True)+"\n);")
    except Exception as err:
      raise Exception("Could not write output. "+str(err))


def main():
  mirrors_file = "mirrors.json"
  private_key = "rootCA/update-center.key"
  public_key = "rootCA/update-center.crt"
  
  original_download_url = "http://updates.jenkins-ci.org/download/"
  original_update_center_url = "https://mirrors.cloud.tencent.com/jenkins/updates/update-center.json"
  original_file = urllib.request.urlopen(original_update_center_url)
  try:
    original_context = original_file.read()
  except http.client.IncompleteRead as e:
    original_context = e.partial.decode('utf-8')
  original = json.loads(original_context.replace(str.encode("updateCenter.post(\n"), str.encode("")).replace(str.encode("\n);"), str.encode("")))
  
  uc = JenkinsUpdateCenter()
  uc.load_private(private_key)
  uc.load_public(public_key)
  uc.warnings = original["warnings"]
  
  try:
    with open(mirrors_file, "r") as fd:
      mirrors_url = json.loads(fd.read())
  except Exception as err:
    raise Exception("Could not load mirrors " + mirrors_file +". " + str(err))

  for site,mirror_url in mirrors_url.items():
    print("Generate:", mirror_url)
    uc.plugins = json.loads(json.dumps(original["plugins"]).replace(original_download_url, mirror_url))
    uc.core = json.loads(json.dumps(original["core"]).replace(original_download_url, mirror_url))
    if not os.path.exists(site):
      os.makedirs(site)
    with open("updates/" + site + "/update-center.json", "w") as fd:
      uc.out(fd)


if __name__ == '__main__':
  main()
