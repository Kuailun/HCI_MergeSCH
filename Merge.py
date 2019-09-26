import Utils
import logging

# Specify File Path
SourceSchFileName_1="C:\\Users\\Yuchen Chai\\Documents\\EAGLE\projects\\Merge\\SparkFun_IMU_Breakout_ICM-20948.sch"
SourceSchFileName_2="C:\\Users\\Yuchen Chai\\Documents\\EAGLE\\projects\\Merge\\SparkFun_Level_Translator_PCA9306.sch"
DestinationSchFileName="C:\\Users\\Yuchen Chai\\Documents\\EAGLE\\projects\\Merge\\Merge.sch"
Path_DataLog="C:\\Users\\Yuchen Chai\\Documents\\EAGLE\\projects\\Merge"

'''Logging设置'''
with open(Path_DataLog+"\\Log.txt",'w') as f:
    f.close()
logger=logging.getLogger("main")
logger.setLevel(level=logging.INFO)
handler=logging.FileHandler(Path_DataLog+"\\Log.txt")
handler.setLevel(logging.INFO)
formatter=logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
console=logging.StreamHandler()
console.setLevel(logging.INFO)
console.setFormatter(formatter)
logger.addHandler(handler)




# Read in Files
file_1=Utils.ReadInXML(SourceSchFileName_1)
file_2=Utils.ReadInXML(SourceSchFileName_2)

# Parse and Merge Files
newXML=Utils.MergeXML(file_1,file_2)

# Beautify the xml
newXML=Utils.prettyXml(newXML,'\t','\n')

# Save XML File
Utils.SaveXML(newXML,DestinationSchFileName)


