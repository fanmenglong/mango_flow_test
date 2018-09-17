import json
import requests
from multiprocessing import Process
import time
import os

__author__ = "Lone"

class FlowTest:
    """
    :param
    urlClose:挂断url
    url:对话url
    token:账号凭证
    token_key:token_key
    flow_id:流程id
    appid:机器人id
    user_id:用户id
    path:配置文件路径
    filename:配置文件名字

    """
    def __init__(self, urlClose, url, token, token_key, flow_id, appid, user_id, configPath, filename):
        self.__token = token
        self.__token_key = token_key
        self.__flow_id = flow_id
        self.__appid = appid
        self.__user_id = user_id
        self.__logPath = configPath[:-7]
        self.__filename = filename
        self.__urlClose = urlClose
        self.__url = url
        self.__configPath = configPath

    def calpercent(self):
        #print(self.__logPath)
        data = {
            'token': self.__token,
            'token_key': self.__token_key,
            'flow_id': self.__flow_id,
            'appid': self.__appid,
            'user_id': self.__user_id,
            'input': ''
        }

        urlClose = self.__urlClose   #http://47.94.197.104/flow/close.do
        url = self.__url   #"http://47.94.197.104/flow/execute.do"
        requests.post(urlClose, json=data)
        file = open(self.__configPath+self.__filename, "r", encoding='UTF-8-sig')
        msg = file.readlines()
        print(self.__filename, msg)
        file.close()
        wish = []
        resTruth = []
        isFlowOutput = []
        for i in msg:
            mes = i.split('=')
            data['input'] = mes[0]
            wish.append(mes[1][0:-1])

            response = requests.post(url, json=data)
            res = response.json()
            resTruth.append(res['info'][0]['output'])
            isFlowOutput.append(res['info'][0]['is_flow_output'])

        standardCount = 0
        semanticsCount = 0
        for i in range(1, len(wish)):
            print(wish[i])
            print(resTruth[i])
            print(isFlowOutput[i])
            if wish[i] == resTruth[i]:
                standardCount = standardCount+1

            if wish[i] == resTruth[i] and isFlowOutput[i]:
                #print(isFlowOutput[i])
                semanticsCount = semanticsCount+1

            # if isFlowOutput[i] == False:
            #     print(wish[i])
            #     print(resTruth[i])
            #     print(isFlowOutput[i])

            if wish[i] != resTruth[i] and isFlowOutput[i] == False:
                print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~BUG error~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
                log = open(self.__logPath + "log.txt", "a")
                log.writelines('——————————————————————————————————————————' + '\n')
                log.writelines('注意！此处服务器回复有误并且发生语义错误！！！错误发生在第'+str(i+1)+'次回复'+'\n')
                log.writelines('预期回复为:' + wish[i] + '\n')
                log.writelines('收到的回复:' + resTruth[i] + '\n')
                log.writelines('——————————————————————————————————————————' + '\n')
                log.close()

            if wish[i] != resTruth[i] and isFlowOutput[i]:
                print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~response error~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
                log = open(self.__logPath + "log.txt", "a")
                log.writelines('——————————————————————————————————————————' + '\n')
                log.writelines('注意！此处服务器回复有误！！！错误发生在第'+str(i+1)+'次回复'+'\n')
                log.writelines('预期回复为:' + wish[i] + '\n')
                log.writelines('收到的回复:' + resTruth[i] + '\n')
                log.writelines('——————————————————————————————————————————' + '\n')
                log.close()

        standardRightPercent = standardCount/((len(wish))-1)
        semanticsRightPercent = semanticsCount/((len(wish))-1)

        log = open(self.__logPath + "log.txt", "a")
        log.writelines('配置文件' + self.__filename + '测试结果如下：\n')
        log.writelines('本次测试标准正确率:'+str(standardRightPercent)+'\n')
        log.writelines('本次测试语义正确率:'+str(semanticsRightPercent)+'\n')
        log.writelines('\n' + '——————————————next——————————————————' + '\n\n')
        log.close()
        # print("标准正确率为", standardRightPercent)
        # print("语义正确率为", semanticsRightPercent)
        return standardRightPercent, semanticsRightPercent

    # def stress_test(self, count):
    #     #print(count)
    #     rate = 0
    #     #for i in range(count):
    #     if self.calpercent() == 1:
    #         rate = 1
    #     else:
    #         log = open(self.__path + "log.txt", "a")
    #         log.writelines("压力测试在第"+str(i+1)+"次失败\n")
    #         log.close()
    #     # rate = rate / count
    #     # log = open(self.__path + "log.txt", "a")
    #     # log.writelines('本次压力测试成功率:' + str(rate*100) + '%\n')
    #     # log.writelines('\n' + '——————————————next——————————————————' + '\n\n')
    #     # log.close()
    #     print(rate)
    #     return rate

def getDirName(path):
    dirNum = 0
    dirList = []
    dirs = os.listdir(path)

    for d in dirs:
        if(os.path.isdir(path+""+d)):
            dirList.append(d)
            dirNum += 1
    return dirNum, dirList

def getFileName(path):
    """读取目录下的所有文件及文件个数"""
    fileNum = 0
    fileList = []
    files = os.listdir(path)
    #print(files)
    for f in files:
        if(os.path.isfile(path+""+f)):
            fileList.append(f)
            fileNum += 1
    return fileNum, fileList

def runProcess(dirL):
    startTime = time.time()

    pathDir = "/data/"
    path = pathDir+dirL+"/"
    #print(path)
    filename = "info.txt"
    info = []
    """读取流程info"""
    with open(path + filename, "r") as file:
        info = file.readlines()
    print("配置文件文件夹", info[7][0:-1])
    """获取流程配置文件"""
    fileNum, fileList = getFileName(info[7][0:-1])
    print("-------配置文件个数及名称\n", fileNum, fileList)
    sRightPercent = 0
    ssRightPercent = 0
    sCount = 0
    ssCount = 0
    for fileN in fileList:
        """处理windows导入文件编码问题"""
        #os.system("enca -L zh_CN -x utf-8 " + info[7][0:-1] + fileN)
        flowTest = FlowTest(info[0][0:-1], info[1][0:-1],
                            info[2][0:-1], info[3][0:-1],
                            info[4][0:-1], info[5][0:-1],
                            info[6][0:-1], info[7][0:-1],
                            fileN)
        standardRightPercent, semanticsRightPercent = flowTest.calpercent()
        sCount = sCount+standardRightPercent
        ssCount = ssCount+semanticsRightPercent

    sRightPercent = sCount/fileNum
    ssRightPercent = ssCount/fileNum
    print()
    print('流程' + dirL + '测试结果如下：')
    print("----------标准正确率为", sRightPercent)
    print("----------语义正确率为", ssRightPercent)
    print()
    log = open(path + "log.txt", "a")
    log.writelines('流程' + dirL + '测试结果如下：\n')
    log.writelines('标准正确率:' + str(sRightPercent) + '\n')
    log.writelines('语义正确率:' + str(ssRightPercent) + '\n')
    log.writelines('\n' + '——————————————next——————————————————' + '\n\n')
    log.close()

    endtime = time.time()
    print("Running Time:", endtime - startTime)


def runTest():
    """多进程运行测试（每个流程一个进程）"""
    pathDir = "/data/"
    dirNum, dirList = getDirName(pathDir)
    print("--------data文件夹个数及名称：\n", dirNum, dirList)
    for dirL in dirList:
        #runProcess(dirL)
        p = Process(target=runProcess, args=(dirL, ))
        p.start()
        #p.join()

if __name__ == '__main__':

    runTest()



    """单个文件Debug"""
    # flowTest = FlowTest("http://60.205.86.31/flow/close.do", "http://60.205.86.31/flow/execute.do",
    #                     "6dc7ea2db072b5316f5ccec00c9533269ea212e0", "ZWH",
    #                     "1587f716ce9e246a8fb85fd8d055652c", "0e769fb38400542eccee4b6a22b9e5ed",
    #                     "2102e9f34c2e628b20aef40fa0104500", "/data/1587f716ce9e246a8fb85fd8d055652c/config/",
    #                     "_15.txt")
    #
    # flowTest.calpercent()


