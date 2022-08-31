import re
import tkinter as tk
from tkinter import END, BooleanVar, StringVar,messagebox
import mysql.connector
from tkinter import ttk,filedialog
import requests,bs4
from matplotlib import pyplot as plt
import pandas as pd
import numpy as np
import base64
from PIL import Image,ImageTk
import io
from tkinter.messagebox import showerror, showinfo, showwarning
from linebot import LineBotApi
from linebot.models import TextSendMessage

#----------一堆設定----------
#houseID, city, area, houseaddress, lease, leasebegins, leaseends, rent, deposit, discount, registrantID, createtime, updatetime

WIDTH = 800
HIGHT = 400
browse_dict = {'city':'縣市','area':'區域','houseaddress':'地址', 'lease':'出租中', 'leasebegins':"出租日", 'leaseends':'退租日', 'rent':'租金', 'deposit':'押金', 'discount':'折扣', "registrant":"招租人",'releasedate':'上傳日期'}
updata_dict = {'houseaddress':'地址', 'rent':'租金', 'deposit':'押金', 'discount':'折扣',"registrant":"使用者代碼"}#我不希望招租人可以更改出租中的資料，到時候必須加入這個功能#'releasedate':'更新日期'
browse_list = ['city','area','houseaddress', 'lease', 'leasebegins', 'leaseends', 'rent', 'deposit', 'discount', "registrant",'releasedate']#宣告也許要改成直接抓資料庫的名稱，不然更改會很麻煩，但我又不想全抓坑
user_browse_dict = {'city':'縣市','area':'區域','houseaddress':'地址','rent':'租金', 'deposit':'押金',"registrant":"招租人"}
user_browse_list = ['city','area','houseaddress','rent', 'deposit',"registrant"]
plot_name_dict = {"area":"區域","rent":"租金","registrant":"招租人"}
user_info_list = ['姓名','方便聯絡時間','連絡電話','line']
img_frame_list = ["image1","image2","image3"]
line_bot_api = LineBotApi('你的TOKEN')
yourID = '你的ID'
taipei_dict = {"台北市":"台北市/?cid=0000",
"中正區":"台北市_中正區/?cid=0000&aid=1",
"大同區":"台北市_大同區/?cid=0000&aid=2",
"中山區":"台北市_中山區/?cid=0000&aid=3",
"松山區":"台北市_松山區/?cid=0000&aid=4",
"大安區":"台北市_大安區/?cid=0000&aid=5",
"萬華區":"台北市_萬華區/?cid=0000&aid=6",
"信義區":"台北市_信義區/?cid=0000&aid=7",
"士林區":"台北市_士林區/?cid=0000&aid=8",
"北投區":"台北市_北投區/?cid=0000&aid=9",
"內湖區":"台北市_內湖區/?cid=0000&aid=10",
"南港區":"台北市_南港區/?cid=0000&aid=11",
"文山區":"台北市_文山區/?cid=0000&aid=12"}
new_taipei_dict = {"新北市":"新北市/?cid=0001",
"萬里區":"新北市_萬里區/?cid=0001&aid=13",
"金山區":"新北市_金山區/?cid=0001&aid=14",
"板橋區":"新北市_板橋區/?cid=0001&aid=15",
"汐止區":"新北市_汐止區/?cid=0001&aid=16",
"深坑區":"新北市_深坑區/?cid=0001&aid=17",
"石碇區":"新北市_石碇區/?cid=0001&aid=18",
"瑞芳區":"新北市_瑞芳區/?cid=0001&aid=19",
"平溪區":"新北市_平溪區/?cid=0001&aid=20",
"雙溪區":"新北市_雙溪區/?cid=0001&aid=21",
"貢寮區":"新北市_貢寮區/?cid=0001&aid=22",
"新店區":"新北市_新店區/?cid=0001&aid=23",
"坪林區":"新北市_坪林區/?cid=0001&aid=24",
"烏來區":"新北市_烏來區/?cid=0001&aid=25",
"永和區":"新北市_永和區/?cid=0001&aid=26",
"中和區":"新北市_中和區/?cid=0001&aid=27",
"三峽區":"新北市_三峽區/?cid=0001&aid=29",
"樹林區":"新北市_樹林區/?cid=0001&aid=30",
"鶯歌區":"新北市_鶯歌區/?cid=0001&aid=31",
"三重區":"新北市_三重區/?cid=0001&aid=32",
"新莊區":"新北市_新莊區/?cid=0001&aid=33",
"泰山區":"新北市_泰山區/?cid=0001&aid=34",
"林口區":"新北市_林口區/?cid=0001&aid=35",
"蘆洲區":"新北市_蘆洲區/?cid=0001&aid=36",
"五股區":"新北市_五股區/?cid=0001&aid=37",
"八里區":"新北市_八里區/?cid=0001&aid=38",
"淡水區":"新北市_淡水區/?cid=0001&aid=39",
"三芝區":"新北市_三芝區/?cid=0001&aid=40",
"石門區":"新北市_石門區/?cid=0001&aid=41"}
# Taipei,Zhongzheng,Datong,Zhongshan,Songshan,DaAn,Wanhua,Xinyi,Shilin,Beitou,Neihu,Nangang,Wenshan = 
data_sql_dict = {
"台北市":"",
"中正區":"",
"大同區":"",
"中山區":"",
"松山區":"",
"大安區":"",
"萬華區":"",
"信義區":"",
"士林區":"",
"北投區":"",
"內湖區":"",
"南港區":"",
"文山區":""}
city_dict = {"台北市":taipei_dict,"新北市":new_taipei_dict}
registrantID_dict = {"112358":"王思詠","blank666":"布蘭克"}

#----------基本宣告----------
def f5():
    all = browse_view.get_children()#.get_children 抓取所有的children
    for i in all:#逐一刪除
        browse_view.delete(i)
    try:
        db_connect = mysql.connector.connect(host = "localhost",user = "root",password = "gr354517",db = "room_system")
        db_cursor = db_connect.cursor()
        #sql = "SELECT * FROM room_system.house;"
        sql = '''select house.houseID, house.city, house.area, house.houseaddress, house.lease, house.leasebegins, house.leaseends, house.rent, house.deposit, house.discount, registrant.Name, house.createtime, house.updatetime
        from house,registrant
        where house.registrantID = registrant.registrantID'''
        db_cursor.execute(sql)
        rows = db_cursor.fetchall()
        for houseID,*date in rows:#rows is list
            browse_view.insert("",index=houseID,text=str(houseID),values=(date))
        #browse_view.insert('',index=1,text="01",values=(lsit))
        print("成功")
    except:
        print("失敗")
def user_f5():
    all = user_browse_view.get_children()#.get_children 抓取所有的children
    for i in all:#逐一刪除
        user_browse_view.delete(i)
    try:
        db_connect = mysql.connector.connect(host = "localhost",user = "root",password = "gr354517",db = "room_system")
        db_cursor = db_connect.cursor()
        user_f5_sql = '''select house.houseID, house.city, house.area, house.houseaddress, house.rent, house.deposit, registrant.Name
        from house,registrant
        where house.registrantID = registrant.registrantID'''
        db_cursor.execute(user_f5_sql)
        rows = db_cursor.fetchall()
        for houseID,*date in rows:#rows is list
            user_browse_view.insert("",index=houseID,text=str(houseID),values=(date))
        print("成功")
    except:#user_browse_dict = {'city':'縣市','area':'區域','houseaddress':'地址','rent':'租金', 'deposit':'押金',"registrant":"招租人"}
        print("失敗")
def remove():
    selects = browse_view.selection()#取得選擇的目標
    if selects == ():
        messagebox.showwarning("使用提示","請選擇要刪除的項目")
        return
    if registrantID_var.get()  not in list(registrantID_dict.keys()):
        messagebox.showwarning("使用提示","使用者代碼錯誤")
        return
    else:
        try:
            db_connect = mysql.connector.connect(host = "localhost",user = "root",password = "gr354517",db = "room_system")
            db_cursor = db_connect.cursor()
            for select in selects:#從目標中提取個別的值
                check_ID = int(browse_view.item(select,option="text"))#不指定option就會回傳一個字典
                check_sql = f'''select house.houseID,registrant.registrantID, registrant.Name
                from house join registrant on house.registrantID = registrant.registrantID
                where house.houseID ={check_ID}'''# and house.registrantID ="{}"
                db_cursor.execute(check_sql)
                rows = db_cursor.fetchall()
                for houseID, registrantID, Name in rows:
                    if registrantID != registrantID_var.get():
                        messagebox.showwarning("使用提示","僅能更改自身上架之房屋")
                        return
        except:
            print("失敗")
    try:
        db_connect = mysql.connector.connect(host = "localhost",user = "root",password = "gr354517",db = "room_system")
        db_cursor = db_connect.cursor()
        for select in selects:#從目標中提取個別的值
            remove_ID = int(browse_view.item(select,option="text"))#不指定option就會回傳一個字典
            del_sql = f"delete from room_system.house where houseID = {remove_ID}"
            db_cursor.execute(del_sql)
        db_connect.commit()
        print("成功")
        messagebox.showinfo("成功","刪除成功!")
    except:
        print("失敗")
    f5()
def renew(event):
    selects = browse_view.selection()
    #現在我想把資料庫的內容輸出到Entry供使用者參考
    houseaddress_entry.delete(0,END)
    rent_entry.delete(0,END)
    deposit_entry.delete(0,END)
    discount_entry.delete(0,END)
    #releasedate_entry.delete(0,END)
    try:
        db_connect = mysql.connector.connect(host = "localhost",user = "root",password = "gr354517",db = "room_system")
        db_cursor = db_connect.cursor()
        for select in selects:
            re_ID = int(browse_view.item(select,option="text"))
            re_sql = f"""select house.houseaddress, house.rent, house.deposit, house.discount
            from house
            where houseID =  {re_ID}"""
            db_cursor.execute(re_sql)#感覺可以直接抓剛剛treeview的資料整天連資料庫有夠鳥
            rows = db_cursor.fetchall()#blob新增的話要更改
            for houseaddress, rent, deposit, discount in rows:
                houseaddress_entry.insert(0,str(houseaddress))
                rent_entry.insert(0,str(rent))
                deposit_entry.insert(0,str(deposit))
                discount_entry.insert(0,str(discount))
                #registrantID_entry.insert(0,str())
                #releasedate_entry .insert(0,str(releasedate))
        print("成功")#暫時OK
    except:
        print("失敗")
def update():
    selects = browse_view.selection()
    if selects == ():
        messagebox.showwarning("使用提示","請選擇要修改的項目")
        return
    if registrantID_var.get() not in list(registrantID_dict.keys()):
        messagebox.showwarning("使用提示","使用者代碼錯誤")
        return
    else:
        try:
            db_connect = mysql.connector.connect(host = "localhost",user = "root",password = "gr354517",db = "room_system")
            db_cursor = db_connect.cursor()
            for select in selects:#從目標中提取個別的值
                check_ID = int(browse_view.item(select,option="text"))#不指定option就會回傳一個字典
                check_sql = f'''select house.houseID,registrant.registrantID, registrant.Name
                from house join registrant on house.registrantID = registrant.registrantID
                where house.houseID ={check_ID}'''# and house.registrantID ="{}"
                db_cursor.execute(check_sql)
                rows = db_cursor.fetchall()
                for houseID, registrantID, Name in rows:
                    if registrantID != registrantID_var.get():
                        messagebox.showwarning("使用提示","僅能更改自身上架之房屋")
                        return
        except:
            print("失敗")
    for select in selects:
        update_ID = int(browse_view.item(select,option="text"))
    try:
        db_connect = mysql.connector.connect(host = "localhost",user = "root",password = "gr354517",db = "room_system")
        db_cursor = db_connect.cursor()
        print(houseaddress_var.get(),rent_var.get(),deposit_var.get(),discount_var.get())
        re_sql = f"""update room_system.house
        set houseaddress = "{houseaddress_var.get()}",
        rent = {rent_var.get()},
        deposit = {deposit_var.get()},
        discount = {discount_var.get()}
        where houseID = {update_ID}"""
        db_cursor.execute(re_sql)
        db_connect.commit()
        print("成功")
        f5()
        """update room_system.house
        set houseaddress = {houseaddress_var.get()},
        rent = {rent_var.get()},
        deposit = {deposit_var.get()},
        discount = {discount_var.get()}
        where houseID = {re_ID}"""
    except Exception as e:
        print(e.__class__.__name__)
        print("失敗")
def validate_int(var):
    try:
        if var.get()>=0:
            return True
        elif var.get()<0:
            tk.messagebox.showwarning("輸入錯誤","請輸入大於0的數字")
            return False
    except Exception as e:
        tk.messagebox.showwarning("輸入錯誤","請輸入數字")
        return False
def validate_address(var):
    if len(var.get()) <= 6:
        tk.messagebox.showwarning("格式錯誤","請輸入完整地址")
def fuck_tk(entry):
    entry.delete(0,END)
    entry.insert(0,0)
'''def switch_frame(frame:str):
    for i,j in frame_dict.items():
        j.destroy()
    frame_dict[frame].master = window
    frame_dict[frame].grid(row=0,column=0)'''
def switch_frame(frame_name:str):
    '''Show a frame for the given page name'''
    frame = frame_dict[frame_name]
    frame.tkraise()
    f5()
    user_f5()
def add_house():
    if registrantID_var.get()  not in list(registrantID_dict.keys()):
        messagebox.showwarning("使用提示","使用者代碼錯誤")
        return
    area_rule = "^(\w\w市)(\w\w區)"
    area = re.search(area_rule,houseaddress_var.get())
    if area.group(1) not in list(city_dict.keys()):
        messagebox.showwarning("使用提示","地址輸入錯誤")
        return
    #print(area.group(1),area.group(2))
    if len(houseaddress_var.get()) <=6:
        showwarning("輸入錯誤","請確認地址")
        return
    try:
        db_connect = mysql.connector.connect(host = "localhost",user = "root",password = "gr354517",db = "room_system")
        db_cursor = db_connect.cursor()
        sql_house = f'''insert room_system.house (city,area,houseaddress,rent, deposit,discount,registrantID) values("{area.group(1)}","{area.group(2)}","{houseaddress_var.get()}",{rent_var.get()},{deposit_var.get()},{discount_var.get()},"{registrantID_var.get()}")'''
        db_cursor.execute(sql_house)
        db_connect.commit()
        showinfo("上傳成功","上傳成功")
        f5()
    except:
        showerror("上傳失敗","請聯絡技術人員")
def area_f5(event):
    all = browse_view.get_children()#.get_children 抓取所有的children
    for i in all:#逐一刪除
        browse_view.delete(i)
    city = city_dict[city_combo.get()]
    area_combo["values"] = list(city.keys())
    try:
        db_connect = mysql.connector.connect(host = "localhost",user = "root",password = "gr354517",db = "room_system")
        db_cursor = db_connect.cursor()
        city_sql = f'''select house.houseID, house.city, house.area, house.houseaddress, house.lease, house.leasebegins, house.leaseends, house.rent, house.deposit, house.discount, registrant.Name, house.createtime, house.updatetime
        from house join registrant on house.registrantID = registrant.registrantID
        where city = "{city_combo.get()}"'''
        db_cursor.execute(city_sql)
        rows = db_cursor.fetchall()
        for houseID,*date in rows:#rows is list
            browse_view.insert("",index=houseID,text=str(houseID),values=(date))
        #browse_view.insert('',index=1,text="01",values=(lsit))
        print("成功")
    except:
        print("失敗")
def price_f5(event="event"):
    all = browse_view.get_children()#.get_children 抓取所有的children
    for i in all:#逐一刪除
        browse_view.delete(i)
    city = city_dict[city_combo.get()]
    try:
        db_connect = mysql.connector.connect(host = "localhost",user = "root",password = "gr354517",db = "room_system")
        db_cursor = db_connect.cursor()
        area_sql = f'''select house.houseID, house.city, house.area, house.houseaddress, house.lease, house.leasebegins, house.leaseends, house.rent, house.deposit, house.discount, registrant.Name, house.createtime, house.updatetime
        from house join registrant on house.registrantID = registrant.registrantID
        where area = "{area_combo.get()}"'''
        city_sql = f'''select house.houseID, house.city, house.area, house.houseaddress, house.lease, house.leasebegins, house.leaseends, house.rent, house.deposit, house.discount, registrant.Name, house.createtime, house.updatetime
        from house join registrant on house.registrantID = registrant.registrantID
        where city = "{city_combo.get()}"'''
        if area_combo.get() == city_combo.get():
            db_cursor.execute(city_sql)
        else:
            db_cursor.execute(area_sql)
        rows = db_cursor.fetchall()
        for houseID,*date in rows:#rows is list
            browse_view.insert("",index=houseID,text=str(houseID),values=(date))
        print("成功")
    except Exception as e:
        print(str(e))
        print("失敗")
    url = f"https://rent.housefun.com.tw/rentprice/region/{city[area_combo.get()]}"#city_dict 
    headers = {"User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36"}
    web_obj = requests.get(url,headers=headers)
    web_obj.raise_for_status()
    soup_obj = bs4.BeautifulSoup(web_obj.text,'lxml')
    avg_price = soup_obj.select("span.num")#刊登&成交
    avg_price_make_deal["text"] = f"{area_combo.get()} 平均刊登價格:{avg_price[0].text}\n{area_combo.get()} 平均成交價格:{avg_price[1].text}"
def plot_select():
    if plot_select_var.get() =="area":
        generate_bar_rent(plot_select_var.get())
    elif plot_select_var.get() =="rent":
        generate_bar_rent(plot_select_var.get())
    elif plot_select_var.get() =="registrant":
        generate_bar_rent(plot_select_var.get())
def generate_bar_rent(select:str):
    print(select)
    check_list = ""
    rent_columns_list = []
    for i in check_area_var_dict:
        if check_area_var_dict[i].get() == True:
            check_list = check_list + f"'{i}',"
            rent_columns_list.append(i)
    check_list = check_list[0:-1]
    plt.figure(check_list)
    try:
        db_connect = mysql.connector.connect(host = "localhost",user = "root",password = "gr354517",db = "room_system")
        db_cursor = db_connect.cursor()
        data_sql = f'''select house.area,house.rent,registrant.Name
        from house join registrant on house.registrantID = registrant.registrantID
        where city = "台北市" and area in ({check_list})'''
        db_cursor.execute(data_sql)
        df = pd.DataFrame(db_cursor.fetchall(),columns=["area","rent","registrant"])
        xbartender = np.arange(len(df[select].value_counts().index))
        plt.bar(xbartender,df[select].value_counts().values)
        plt.title(check_list)
        plt.yticks([0,1,2,3,4,5,6,7,8])
        plt.xticks(xbartender,df[select].value_counts().index)
        plt.rcParams['font.sans-serif'] = ['Microsoft YaHei']
        plt.show()
        print("成功")
    except Exception as e:
        print(str(e))
        print("失敗")
def all_select():
    if check_area_var_dict["台北市"].get():
        for i,j in cbtn_dict.items():
            j.select()
    else:
        for i,j in cbtn_dict.items():
            j.deselect()
def contact_registrant():
    selects = user_browse_view.selection()
    if selects == ():
        messagebox.showwarning("使用提示","請選擇有興趣的物件")
        return
    user_name = user_info_var_dict["姓名"].get()
    phone = user_info_var_dict["連絡電話"].get()
    if user_name == "":
        messagebox.showwarning("使用提示","姓名不得為空")
        return
    if len(phone) != 10:
        messagebox.showwarning("使用提示","連絡電話格式不符")
        return
    db_connect = mysql.connector.connect(host = "localhost",user = "root",password = "gr354517",db = "room_system")
    db_cursor = db_connect.cursor()
    for select in selects:#從目標中提取個別的值
        house_ID = int(user_browse_view.item(select,option="text"))#不指定option就會回傳一個字典
        sql = f"""select house.houseID,house.houseaddress,house.rent
        from house
        where house.houseID = {house_ID}"""
        try:
            db_cursor.execute(sql)
            rows = db_cursor.fetchall()
            for houseID,houseaddress,rent in rows:
                house_msg = f"""您的房屋有租客感興趣喔!\n編號:{houseID}\n地址:{houseaddress}\n租金:{rent}\n\姓名:{user_name}\n連絡電話:{phone}\nline:{user_info_var_dict["line"].get()}\n方便聯絡時間:{user_info_var_dict["方便聯絡時間"].get()}"""
                line_bot_api.push_message(yourID,TextSendMessage(text=house_msg))
                print("成功")
        except Exception as e:
            print(str(e))
    #user_info_var_dict
    #line_bot_api.push_message(yourID,TextSendMessage(text='測試'))
    #user_info_list = ['姓名','方便聯絡時間','連絡電話','line']
def user_city_f5(event="event"):
    all = user_browse_view.get_children()#.get_children 抓取所有的children
    for i in all:#逐一刪除
        user_browse_view.delete(i)
    city = city_dict[user_city_combo.get()]
    user_area_combo["values"] = list(city.keys())
    try:
        db_connect = mysql.connector.connect(host = "localhost",user = "root",password = "gr354517",db = "room_system")
        db_cursor = db_connect.cursor()
        city_sql = f'''select house.houseID, house.city, house.area, house.houseaddress, house.rent, house.deposit, registrant.Name
        from house join registrant on house.registrantID = registrant.registrantID
        where city = "{user_city_combo.get()}"'''
        db_cursor.execute(city_sql)
        rows = db_cursor.fetchall()
        for houseID,*date in rows:
            user_browse_view.insert("",index=houseID,text=str(houseID),values=(date))
        print("成功")
    except:
        print("失敗")
def user_area_f5(event="event"):
    all = user_browse_view.get_children()#.get_children 抓取所有的children
    for i in all:#逐一刪除
        user_browse_view.delete(i)
    city = city_dict[user_city_combo.get()]
    try:
        db_connect = mysql.connector.connect(host = "localhost",user = "root",password = "gr354517",db = "room_system")
        db_cursor = db_connect.cursor()
        area_sql = f'''select house.houseID, house.city, house.area, house.houseaddress, house.rent, house.deposit, registrant.Name
        from house join registrant on house.registrantID = registrant.registrantID
        where area = "{user_area_combo.get()}"'''
        city_sql = f'''select house.houseID, house.city, house.area, house.houseaddress, house.rent, house.deposit, registrant.Name
        from house join registrant on house.registrantID = registrant.registrantID
        where city = "{user_city_combo.get()}"'''
        if user_area_combo.get() == user_city_combo.get():
            db_cursor.execute(city_sql)
        else:
            db_cursor.execute(area_sql)
        rows = db_cursor.fetchall()
        for houseID,*date in rows:#rows is list
            user_browse_view.insert("",index=houseID,text=str(houseID),values=(date))
        print("成功")
    except Exception as e:
        print(str(e))
        print("失敗")
def upload_image():
    selects = browse_view.selection()
    if selects == ():
        messagebox.showwarning("使用提示","請選擇需要上傳圖片的物件")
        return
    if registrantID_var.get()  not in list(registrantID_dict.keys()):
        messagebox.showwarning("使用提示","使用者代碼錯誤")
        return
    else:
        try:
            db_connect = mysql.connector.connect(host = "localhost",user = "root",password = "gr354517",db = "room_system")
            db_cursor = db_connect.cursor()
            for select in selects:#從目標中提取個別的值
                check_ID = int(browse_view.item(select,option="text"))#不指定option就會回傳一個字典
                check_sql = f'''select house.houseID,registrant.registrantID, registrant.Name
                from house join registrant on house.registrantID = registrant.registrantID
                where house.houseID ={check_ID}'''# and house.registrantID ="{}"
                db_cursor.execute(check_sql)
                rows = db_cursor.fetchall()
                for houseID, registrantID, Name in rows:
                    if registrantID != registrantID_var.get():
                        messagebox.showwarning("使用提示","僅能更改自身上架之房屋")
                        return
        except:
            print("失敗")
    show_img = tk.Toplevel(window)
    show_img.title("圖片上傳")
    IMG1_upload_btn = tk.Button(show_img,text="IMG1_upload",width=8,font=12,command=lambda:choose_image("IMG1"))
    IMG2_upload_btn = tk.Button(show_img,text="IMG2_upload",width=8,font=12,command=lambda:choose_image("IMG2"))
    IMG3_upload_btn = tk.Button(show_img,text="IMG3_upload",width=8,font=12,command=lambda:choose_image("IMG3"))
    IMG1_show_btn = tk.Button(show_img,text="IMG1_show",width=8,font=12,command=lambda:show_image("IMG1"))
    IMG2_show_btn = tk.Button(show_img,text="IMG2_show",width=8,font=12,command=lambda:show_image("IMG2"))
    IMG3_show_btn = tk.Button(show_img,text="IMG3_show",width=8,font=12,command=lambda:show_image("IMG3"))
    IMG1_del_btn = tk.Button(show_img,text="IMG1_del",width=8,font=12,command=lambda:del_image("IMG1"))
    IMG2_del_btn = tk.Button(show_img,text="IMG2_del",width=8,font=12,command=lambda:del_image("IMG2"))
    IMG3_del_btn = tk.Button(show_img,text="IMG3_del",width=8,font=12,command=lambda:del_image("IMG3"))
    IMG1_upload_btn.grid(row=1,column=0)
    IMG2_upload_btn.grid(row=1,column=1)
    IMG3_upload_btn.grid(row=1,column=2)
    IMG1_show_btn.grid(row=0,column=0)
    IMG2_show_btn.grid(row=0,column=1)
    IMG3_show_btn.grid(row=0,column=2)
    IMG1_del_btn.grid(row=2,column=0)
    IMG2_del_btn.grid(row=2,column=1)
    IMG3_del_btn.grid(row=2,column=2)
def choose_image(column):
    print(column)
    selects = browse_view.selection()
    IMG_PATH = filedialog.askopenfilename(filetypes=[("iamge file",(".jpg",".png",".gif",".jpeg")),("All files", ".*")])
    IMG_OBJ = open(IMG_PATH,mode="rb")
    IMG_blob = IMG_OBJ.read()
    IMG_base64 = base64.b64encode(IMG_blob)
    db_connect = mysql.connector.connect(host = "localhost",user = "root",password  = "gr354517",db = "room_system")
    db_cursor = db_connect.cursor()
    for select in selects:#從目標中提取個別的值
        house_ID = int(browse_view.item(select,option="text"))
        upload_sql = f"""update room_system.house
        set {column} = "{str(IMG_base64,encoding="utf-8")}"
        where houseID = {house_ID}"""
        try:
            db_cursor.execute(upload_sql)
            db_connect.commit()
            print("成功")
        except Exception as e:
            print(str(e))
            print("失敗")
def show_image(column):
    selects = browse_view.selection()
    db_connect = mysql.connector.connect(host = "localhost",user = "root",password  = "gr354517",db = "room_system")
    db_cursor = db_connect.cursor()
    for select in selects:#從目標中提取個別的值
        show_ID = int(browse_view.item(select,option="text"))
        show_sql = f"""SELECT {column}
        FROM room_system.house
        where houseID = {show_ID}"""
        try:
            db_cursor.execute(show_sql)
            rows = db_cursor.fetchall()
            for IMG_data in rows:
                for IMG_64 in IMG_data:
                    if type(IMG_64) == type(None):
                        showinfo("使用提示","沒有圖片，有需要請上傳圖片")
                        return
                    IMG_bytes = base64.b64decode(IMG_64)#這東西已經跟當初用二進位方式讀 取的一樣了
                    IMG_PIL = Image.open(io.BytesIO(IMG_bytes))#變回pil_image
                    IMG_TK = ImageTk.PhotoImage(IMG_PIL)#變回tk_image
                    IMG_PIL.show()
                    #IMG_TK.show()
                    print('成功')
        except Exception as e:
            print(str(e))

    
def small_img(img,target_height=300,target_width=300):
    x,y = img.size
    if (x/y) >(target_height/target_width):
        y = y*(target_height/x)
        img = img.resize((target_height,int(y)))
    else:
        x = x*(target_width/x)
        img = img.resize((int(x),target_width))
    return img
def del_image(column):
    selects = browse_view.selection()
    db_connect = mysql.connector.connect(host = "localhost",user = "root",password  = "gr354517",db = "room_system")
    db_cursor = db_connect.cursor()
    for select in selects:#從目標中提取個別的值
        del_ID = int(browse_view.item(select,option="text"))
        del_sql = f"""update room_system.house
        set {column} = null
        where houseID = {del_ID}"""
        try:
            db_cursor.execute(del_sql)
            db_connect.commit()
            print("成功")
        except Exception as e:
            print(str(e))
def user_img_renew(event):
    selects = user_browse_view.selection()
    if selects == ():
        messagebox.showwarning("使用提示","請選擇有興趣的物件")
        return
    db_connect = mysql.connector.connect(host = "localhost",user = "root",password  = "gr354517",db = "room_system")
    db_cursor = db_connect.cursor()
    for select in selects:
        img_renew_ID = int(user_browse_view.item(select,option="text"))
        img_renew_sql = f"""select IMG1,IMG2,IMG3
        from room_system.house
        where houseID = {img_renew_ID}"""
        try:        
            db_cursor.execute(img_renew_sql)
            rows = db_cursor.fetchall()
            for data in rows:
                for i,j in zip(data,img_frame_list):
                    if type(i) == type(None):#
                        blank = Image.new("RGB",(50,50),(0,0,0))
                        blank = ImageTk.PhotoImage(blank)
                        x = tk.Label(user_window)
                        x.photo = blank
                        img_lb_dict[j]["image"] = x.photo
                        continue
                    IMG_b64 = base64.b64decode(i)
                    IMG_b = Image.open(io.BytesIO(IMG_b64))
                    IMG_s = small_img(IMG_b)
                    #IMG_s.show()#測試
                    #IMG = ImageTk.PhotoImage(IMG_s)#不知道為甚麼圖片還是顯示不出來，理論上OK，別處測試也OK
                    x = tk.Label(user_window)
                    x.photo = ImageTk.PhotoImage(IMG_s)#magic!!
                    img_lb_dict[j]["image"] = x.photo
                    print(j,"成功")
        except Exception as e:
            print(str(e))
def select_to_csv():
    check_list = ""
    for i in check_area_var_dict:
        if check_area_var_dict[i].get() == True:
            check_list = check_list + f"'{i}',"
    check_list = check_list[0:-1]
    db_connect = mysql.connector.connect(host = "localhost",user = "root",password = "gr354517",db = "room_system")
    db_cursor = db_connect.cursor()
    PATH = filedialog.asksaveasfile(defaultextension=".csv",filetypes=[("csv file",".csv"),("HTML file", ".html"),("All files", ".*")])
    try:#house.city, house.area, house.houseaddress,house.rent, house.deposit, house.discount,registrant.Name
        data_sql = f'''select house.city, house.area, house.houseaddress,house.rent, house.deposit, house.discount,registrant.Name
        from house join registrant on house.registrantID = registrant.registrantID
        where city = "台北市" and area in ({check_list})'''
        db_cursor.execute(data_sql)
        df = pd.DataFrame(db_cursor.fetchall(),columns=["city","area","houseaddress","rent","deposit","discount","Name"])
        df.to_csv(PATH,encoding="big5",index=False,line_terminator="\n")
        print("成功")
    except Exception as e:
        print(str(e))
def csv_import():
    PATH = filedialog.askopenfilename(filetypes=[("file",".csv")])
    if PATH == "":
        print("沒有選擇檔案")
    #PATHH = "C:\\Users\\王恩詠\\Documents\\自訂 Office 範本\\test2.csv"
    df = pd.read_csv(PATH,encoding="big5")
    df["deposit"] = df["deposit"].fillna(0)
    df["discount"] = df["discount"].fillna(0)#這三個東西還好直接補0
    df["Name"] = df["Name"].fillna(0)
    df.info()
    df_total = len(df)#df總數
    df.info()
    df_na = len(df)-len(df.dropna())#df缺失的數量，這些東西將不會上傳
    df = df.dropna()
    db_connect = mysql.connector.connect(host = "localhost",user = "root",password = "gr354517",db = "room_system")
    db_cursor = db_connect.cursor()
    succes_list = ""
    #fail_list = []
    try:
        for i in df.itertuples():
            import_sql = f"""insert room_system.house (city,area,houseaddress,rent, deposit,discount,registrantID) values("{i[1]}","{i[2]}","{i[3]}",{i[4]},{i[5]},{i[6]},"{registrantID_var.get()}")"""
            succes_list += str(i[3])+"\n"
            db_cursor.execute(import_sql)
            db_connect.commit()
            print(i[3],"成功")
        showinfo("匯入紀錄",f"總共{df_total}\n成功:{succes_list}資料缺失:{df_na}")
        print("成功")
        f5()
    except Exception as e:
        print(str(e))


window = tk.Tk()
window.title("套房系統")
window.geometry()#f"{WIDTH}x{HIGHT}"

container = tk.Frame(window)
container.grid(row=0, column=0, sticky="nsew")

revise_window = tk.Frame(container)
Backstage_window = tk.Frame(container)
user_window = tk.Frame(container)
add_window = tk.Frame(container)

frame_dict = {"revise_window":revise_window,"user_window":user_window,"add_window":add_window,"Backstage_window":Backstage_window}

#----------Menu----------
menubar = tk.Menu(window)

lessee_menubar = tk.Menu(menubar)
lessee_menubar.add_command(label="新增系統",command=lambda:switch_frame("add_window"))
lessee_menubar.add_command(label="修改系統",command=lambda:switch_frame("revise_window"))
lessee_menubar.add_command(label="瀏覽系統",command=lambda:switch_frame("Backstage_window"))

seeker_menubar = tk.Menu(menubar)
seeker_menubar.add_command(label="搜尋系統",command=lambda:switch_frame("user_window"))#frame_state = frame

menubar.add_cascade(label="招租人",menu=lessee_menubar)
menubar.add_cascade(label="尋租人",menu=seeker_menubar)
window.config(menu=menubar)
#----------Menu----------
#----------add_window----------

#----------位置調整----------

#----------add_window----------

#----------revise_window----------
COUNT = 0
for i,j in updata_dict.items():
    tk.Label(revise_window,text=j,font=10).grid(row=3,column=0+COUNT,padx=5,pady=5)#,sticky="E"
    COUNT += 1
revise_f5_btn = tk.Button(revise_window,text="重新整理",width=10,height=1,font=24,padx=3,pady=3,command=f5)
city_combo = ttk.Combobox(revise_window,values=list(city_dict.keys()),width=10)
area_combo = ttk.Combobox(revise_window,width=10)
avg_price_make_deal = tk.Label(revise_window,text="參考價格",width=30)
browse_view_ybar = tk.Scrollbar(revise_window)
browse_view = ttk.Treeview(revise_window,height=10,columns=browse_list,yscrollcommand=browse_view_ybar.set)
for i,j in browse_dict.items():
    browse_view.column(i,width=80,minwidth=50)
    browse_view.heading(i,text=j)
browse_view.column("#0",width=50,minwidth=50)
browse_view.column("houseaddress",width=240,minwidth=50)
browse_view.column("releasedate",width=120,minwidth=50)

del_btn = tk.Button(revise_window,text="刪除",width=10,height=1,font=24,padx=3,pady=3,command=remove)
csv_import_btn = tk.Button(revise_window,text="匯入",width=10,height=1,font=24,padx=3,pady=3,command=csv_import)
upload_image_btn = tk.Button(revise_window,text="上傳圖片",width=10,height=1,font=24,padx=3,pady=3,command=upload_image)
re_btn = tk.Button(revise_window,text="更新",width=10,height=1,font=24,padx=3,pady=3,command=update)#調整
add_btn = tk.Button(revise_window,text="新增",width=10,height=1,font=24,padx=3,pady=3,command=add_house)

houseaddress_var,registrantID_var = tk.StringVar(),tk.StringVar()
rent_var,deposit_var,discount_var = tk.IntVar(),tk.IntVar(),tk.IntVar()
houseaddress_entry = tk.Entry(revise_window,textvariable=houseaddress_var,width=40)
rent_entry = tk.Entry(revise_window,textvariable=rent_var,width=10)
deposit_entry = tk.Entry(revise_window,textvariable=deposit_var,width=10)
discount_entry = tk.Entry(revise_window,textvariable=discount_var,width=10)
registrantID_entry = tk.Entry(revise_window,textvariable=registrantID_var,width=10)
#releasedate_entry = tk.Entry(revise_window,state="disabled",width=14)#還有一點問題，我想讓使用者不能更改這一個文件但要可以系統輸入東西進去

#----------特殊設定----------
city_combo.bind("<<ComboboxSelected>>",area_f5)
area_combo.bind("<<ComboboxSelected>>",price_f5)#<<ComboboxSelected>>選到這個東西時會觸發事件#values=list(taipei_dict.keys())
browse_view.bind("<ButtonRelease-1>",renew)
houseaddress_entry.config(validate="focusout",validatecommand=lambda:validate_address(houseaddress_var))
rent_entry.config(validate="focusout",validatecommand=lambda:validate_int(rent_var),invalidcommand=lambda:fuck_tk(rent_entry))
deposit_entry.config(validate="focusout",validatecommand=lambda:validate_int(deposit_var),invalidcommand=lambda:fuck_tk(deposit_entry))
discount_entry.config(validate="focusout",validatecommand=lambda:validate_int(discount_var),invalidcommand=lambda:fuck_tk(discount_entry))
registrantID_entry.config(show="*")
registrantID_entry.insert(0,"112358")#到時候要刪掉
#----------位置調整----------
revise_f5_btn.grid(row=0,column=0,sticky="W",padx=5,pady=5)
city_combo.grid(row=0,column=1,padx=5,pady=5)
area_combo.grid(row=0,column=2,padx=5,pady=5)
avg_price_make_deal.grid(row=0,column=3,padx=5,pady=5)
browse_view.grid(row=1,column=0,columnspan=5,pady=5)
browse_view_ybar.grid(row=1,column=6,sticky="N"+"S"+"E")
browse_view_ybar.config(command=browse_view.yview)
houseaddress_entry.grid(row=4,column=0,pady=5)
rent_entry.grid(row=4,column=1,pady=5)
deposit_entry.grid(row=4,column=2,pady=5)
discount_entry.grid(row=4,column=3,pady=5)
registrantID_entry.grid(row=4,column=4,pady=5)
#releasedate_entry.grid(row=4,column=4,pady=5)
del_btn.grid(row=5,column=0,sticky="W",padx=5,pady=5)#sticky="W"
csv_import_btn.grid(row=5,column=1,sticky="E",padx=5,pady=5)
upload_image_btn.grid(row=5,column=2,sticky="E",padx=5,pady=5)
re_btn.grid(row=5,column=3,sticky="E",padx=5,pady=5)
add_btn.grid(row=5,column=4,sticky="E",padx=5,pady=5)
#-----------revise_window-----------

#----------user_window-----------
user_f5_btn = tk.Button(user_window,text="重新整理",width=10,height=1,font=24,padx=3,pady=3,command=user_f5)
user_city_combo = ttk.Combobox(user_window,values=list(city_dict.keys()),width=10)
user_area_combo = ttk.Combobox(user_window,width=10)
#city_dict
user_browse_view_ybar = tk.Scrollbar(user_window)
user_browse_view = ttk.Treeview(user_window,height=10,columns=user_browse_list,yscrollcommand=user_browse_view_ybar.set)
for i,j in user_browse_dict.items():
    user_browse_view.column(i,width=80,minwidth=50)
    user_browse_view.heading(i,text=j)
user_browse_view.column("#0",width=50,minwidth=50)
user_browse_view.column("houseaddress",width=240,minwidth=50)
img_note = ttk.Notebook(user_window)
img_frame_dict = {}
img_lb_dict = {}
for i in img_frame_list:
    img_frame_dict[i] = tk.Frame(img_note)
    img_frame_dict[i].grid(row=0,column=0)
    img_note.add(img_frame_dict[i],text=i)
    img_lb_dict[i] = tk.Label(img_frame_dict[i])
    img_lb_dict[i].grid(row=0,column=0)
user_info_obj_dict = {}
user_info_var_dict = {}
COUNT = 0
for i in user_info_list:
    user_info_var_dict[i] = StringVar()
    user_info_obj_dict[i] = (tk.Entry(user_window,textvariable=user_info_var_dict[i],width=10),tk.Label(user_window,text=i,font=10))
    user_info_obj_dict[i][0].grid(row=3,column=0+COUNT,sticky="W",padx=5,pady=5)
    user_info_obj_dict[i][1].grid(row=2,column=0+COUNT,sticky="W",padx=5,pady=5)
    COUNT += 1
#['姓名','方便聯絡時間','連絡電話','line']
#user_info_obj_dict["姓名"][0].config(width=)
user_info_obj_dict["方便聯絡時間"][0].grid(sticky="WE")
contact_btn = tk.Button(user_window,text="聯絡招租人",width=10,height=1,font=24,command=contact_registrant)
user_info_obj_dict["姓名"][0].insert(0,"王思詠")
user_info_obj_dict["方便聯絡時間"][0].insert(0,"12:00")
user_info_obj_dict["連絡電話"][0].insert(0,"0975654611")
user_info_obj_dict["line"][0].insert(0,"0975654611")
user_city_combo.bind("<<ComboboxSelected>>",user_city_f5)
user_area_combo.bind("<<ComboboxSelected>>",user_area_f5)
user_browse_view.bind("<ButtonRelease-1>",user_img_renew)
#----------位置調整----------

user_f5_btn.grid(row=0,column=0,sticky="W",padx=5,pady=5)
user_city_combo.grid(row=0,column=1,padx=5,pady=5)
user_area_combo.grid(row=0,column=2,padx=5,pady=5)
user_browse_view.grid(row=1,column=0,columnspan=5,pady=5)#
user_browse_view_ybar.grid(row=1,column=6,sticky="N"+"S"+"E")
user_browse_view_ybar.config(command=user_browse_view.yview)
img_note.grid(row=1,column=7,sticky="NSWE")
contact_btn.grid(row=3,column=4,sticky="W",padx=5,pady=5)
#----------user_window-----------

#-----------Backstage_window-----------

generate_btn = tk.Button(Backstage_window,text="生成圖片",width=10,height=1,font=24,padx=3,pady=3,command=plot_select)
# check_city_dict = {}
# COUNT = 0
# for i,j in city_dict.items():
#     check_city_dict[i] = BooleanVar()
#     tk.Radiobutton(Backstage_window,text=i,variable=check_city_dict[i],padx=5,pady=5).grid(row=0,column=1+COUNT)
#     COUNT += 1
plot_rbtn_dict = {}
#plot_rbtn_var_dict = {}
COUNT = 0
plot_select_var = StringVar()
for i,j in plot_name_dict.items():
    plot_rbtn_dict[i] = tk.Radiobutton(Backstage_window,text=j,variable=plot_select_var,value=i)
    plot_rbtn_dict[i].grid(row=0,column=1+COUNT)
    COUNT += 1
plot_rbtn_dict["area"].select()#預選一個
check_area_var_dict = {}
cbtn_dict = {}
COUNT = 0
COUNT_X = 0
for i,j in taipei_dict.items():
    check_area_var_dict[i] = BooleanVar()
    if i == "台北市":
        cbtn_dict[i] = tk.Checkbutton(Backstage_window,text=i,variable=check_area_var_dict[i],pady=5,command=all_select,onvalue=True,offvalue=False)
        cbtn_dict[i].grid(row=2+COUNT,column=0+COUNT_X)#,command=all_check
    else:
        cbtn_dict[i] = tk.Checkbutton(Backstage_window,text=i,variable=check_area_var_dict[i],pady=5)
        cbtn_dict[i].grid(row=2+COUNT,column=0+COUNT_X)#locals()[i+"_cbtn"]  = 
    COUNT += 1
    if COUNT == 8:
        COUNT_X += 1
        COUNT = 0
export_btn = tk.Button(Backstage_window,text="匯出",width=10,height=1,font=24,padx=3,pady=3,command=select_to_csv)
#----------位置調整----------
generate_btn.grid(row=0,column=0,sticky="W",padx=5,pady=5)
export_btn.grid(row=9,column=5,sticky="W",padx=5,pady=5)
#-----------Backstage_window-----------
#----------位置調整----------
container.grid(row=0,column=0)
revise_window.grid(row=0, column=0, sticky="nsew")
user_window.grid(row=0, column=0, sticky="nsew")
add_window.grid(row=0, column=0, sticky="nsew")
Backstage_window.grid(row=0, column=0, sticky="nsew")
switch_frame("user_window")
#cbtn_dict["台北市"].select()
user_f5()
f5()
window.mainloop()
plt.close()
print("END")
#----------目前無用----------
def generate_bar_area():#目前無用
    check_list = ""
    area_columns_list = []
    for i in check_area_var_dict:
        if check_area_var_dict[i].get() == True:
            check_list = check_list + f"'{i}',"
            area_columns_list.append(i)
    check_list = check_list[0:-1]
    plt.figure(check_list)
    try:
        db_connect = mysql.connector.connect(host = "localhost",user = "root",password = "gr354517",db = "room_system")
        db_cursor = db_connect.cursor()
        data_sql = f'''select house.area,house.rent
        from house
        where city = "台北市" and area in ({check_list})'''
        db_cursor.execute(data_sql)
        df = pd.DataFrame(db_cursor.fetchall(),columns=["area","rent"])
        
        plt.bar(df["area"].value_counts().index,df["area"].value_counts().values)
        xticks = np.arange(len(df["area"].value_counts().values))
        plt.title(check_list)
        plt.xticks(xticks,df["area"].value_counts().index)
        plt.rcParams['font.sans-serif'] = ['Microsoft YaHei']
        plt.show()
        print("成功")
    except Exception as e:
        print(str(e))
        print("失敗")
