import requests
from bs4 import BeautifulSoup
import json
import hashlib

class qldtAPI:
    def __init__(self):
        self.session = requests.Session()
        self.soup_target = None
        self.element = None
        self.data = None
        self.login_response = None
        self.element_field = None


    #################################################################################################
    # Level1

    def login(self, username, password,target_url):
        # URL của trang đăng nhập
        login_url = "https://qldt.utt.edu.vn/CMCSoft.IU.Web.Info/Login.aspx"

        try:
            print("Đang truy cập vào trang đăng nhập ...")
            # Lấy dữ liệu từ trang đăng nhập
            response = self.session.get(login_url)
            soup = BeautifulSoup(response.text, "html.parser")

            print("Truy cập thành công !")
            # Tìm và mã hóa mật khẩu
            txt_password = soup.find("input", {"id": "txtPassword"})
            md5_password = hashlib.md5(password.encode()).hexdigest()

            # Dữ liệu POST để gửi đến trang đăng nhập
            payload = {
                "__VIEWSTATE": soup.find("input", {"id": "__VIEWSTATE"})["value"],
                "__VIEWSTATEGENERATOR": soup.find("input", {"id": "__VIEWSTATEGENERATOR"})["value"],
                "__EVENTVALIDATION": soup.find("input", {"id": "__EVENTVALIDATION"})["value"],
                "txtUserName": username,
                "txtPassword": md5_password,
                "btnSubmit": "Đăng nhập"
            }

            
            print("Đang gửi yêu cầu POST để đăng nhập...")
            # Gửi yêu cầu POST để đăng nhập
            self.login_response = self.session.post(login_url, data=payload)
            
            # kiểm tra trạng thái đăng nhập
            


            # Truy cập trang sau khi đăng nhập
            print("Đang truy cập vào "+ str(target_url)+" ...")
            target_response = self.session.get(target_url)
            self.soup_target = BeautifulSoup(target_response.text, "html.parser")
            print("Truy cập vào "+ str(target_url)+" thành công!")

        except Exception as e:
            print("Đã xảy ra lỗi:", e)
            return False

    #################################################################################################
    #Level 2 

    def htmlElement(self, element_field, id_value):
        self.element_field = element_field
        self.id_value = id_value
        if self.soup_target:
            # Phân tích nội dung trang sau khi đăng nhập để tìm phần tử
            self.element = self.soup_target.find(element_field, {"id": id_value})

            if self.element:
                print(f"Đã tìm thấy {element_field} có id='{id_value}'!")
                return self.element
            else:
                print(f"Không tìm thấy {element_field} có id='{id_value}'!")
                return None
        else:
            print("Không có dữ liệu để xuất!")
            return None
    
    #################################################################################################
    # Level 3

    # check logged in
    def isLogged_in(self):
        if self.element:
            print(f"Đã tìm thấy {self.element_field} có id='{self.id_value}'!")
            return True
        else:
            print(f"Không tìm thấy {self.element_field} có id='{self.id_value}'!")
            return False

    # get qldt user info
    def getContent(self):
        if self.element:
            print(f"Đã tìm thấy {self.element_field} có id='{self.id_value}'!")
            return self.element.get_text()
        else:
            print(f"Không tìm thấy {self.element_field} có id='{self.id_value}'!")
            return None

    # convert table to json
    def jsonConvert(self):
        # Phân tích nội dung HTML bằng BeautifulSoup
        soup = self.element

        # Tìm tất cả các hàng (rows) trong bảng
        rows = soup.find_all("tr")

        # Tạo danh sách trường từ hàng đầu tiên
        fields = [cell.get_text(strip=True) for cell in rows[0].find_all(["th", "td"])]

        # Khởi tạo danh sách để lưu trữ dữ liệu từ bảng
        self.data = []

        # Lặp qua các hàng bắt đầu từ hàng thứ hai
        for row in rows[1:]:
            # Tìm tất cả các ô (cells) trong hàng
            cells = row.find_all(["th", "td"])
            
            # Khởi tạo từ điển để lưu trữ dữ liệu của hàng hiện tại
            row_data = {}
            
            # Lặp qua từng ô trong hàng và thêm dữ liệu vào từ điển
            for field, cell in zip(fields, cells):
                row_data[field] = cell.get_text(strip=True)
            
            # Thêm dữ liệu của hàng vào danh sách
            self.data.append(row_data)

        path = "student_mark_table.json"
        with open(path, "w", encoding="utf-8") as json_file:
            json.dump(self.data, json_file, indent=4, ensure_ascii=False)

        return self.data

    #################################################################################################
    # Level 4

    def preprocessJson(self,key_field,username):
        self.cleaned_data = []
        id = 0
        for item in self.data:
            id = id+1
            keyField = item.get(key_field, "")
            dbKey = f"{id}_{username}_{keyField}"
            
            # Kiểm tra xem idPHSV có giá trị không và loại bỏ các mục có idPHSV rỗng
            if dbKey:
                item["dbKey"] = dbKey
                self.cleaned_data.append(item)

        path = "student_mark_table.json"    
        with open(path, "w", encoding="utf-8") as json_file:
            json.dump(self.cleaned_data, json_file, indent=4, ensure_ascii=False)

        return self.cleaned_data

username = '73DCHT22'
password = '06/02/2004'
markTableURL = "https://qldt.utt.edu.vn/CMCSoft.IU.Web.Info/StudentMark.aspx"

mark_table = qldtAPI()
mark_table.login(username, password,markTableURL)
mark_table.htmlElement("table", "tblStudentMark")