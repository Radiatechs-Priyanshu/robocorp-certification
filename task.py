"""Template robot with Python."""
from RPA.Excel.Application import Application
from RPA.Excel.Files import Files
from RPA.Browser import Browser
from RPA.HTTP import HTTP
from RPA.Tables import Tables
from RPA.Browser.Selenium import Selenium
from RPA.Archive import Archive
from RPA.PDF import PDF
from RPA.FileSystem import FileSystem
from RPA.Robocloud.Secrets import Secrets
from RPA.Dialogs import Dialogs
import time
import os


browser=Selenium()
# username=""
URL="https://robotsparebinindustries.com/#/robot-order"
order_file_url="https://robotsparebinindustries.com/orders.csv"
def open_the_intranet_website():
    browser.open_available_browser(url=URL)
    

def export_the_table_as_a_pdf(number):
    try:
        sales_results_html = browser.get_element_attribute(locator="id:receipt", attribute="outerHTML")
        pdf = PDF()
        pdf.html_to_pdf(sales_results_html, "pdf/"+str(number)+".pdf")
        browser.capture_element_screenshot(locator="id:robot-preview-image",filename=f"{os.getcwd()}/pdf/"+str(number)+".png")
        pdf.add_files_to_pdf(files=["pdf/"+str(number)+".pdf","pdf/"+str(number)+".png:align=center"],target_document="pdf/"+str(number)+".pdf")
    except Exception as e:
        print(e)
        pass
def create_zip():
    archive = Archive()
    fileSystem = FileSystem()
    archive.archive_folder_with_zip('./pdf', 'output/receipts.zip', recursive=True,include="*.pdf")
    fileSystem.remove_directory("./pdf",recursive=True)

def fill_the_details(orders):
    time.sleep(2)
    browser.click_element_when_visible("id:head")
    browser.click_element_when_visible(locator="//*[@id='head']/option[@value='"+str(orders['Head'])+"']")
    browser.click_element_when_visible(locator="//*[@id='id-body-"+str(orders['Body'])+"']")
    browser.input_text("//*[@id='root']/div/div[1]/div/div[1]/form/div[3]/input",orders['Legs'])
    browser.input_text("id:address",orders['Address'])
    browser.click_element_when_visible("id:preview")
    time.sleep(2)
    while(True):
        try:
            browser.click_element_when_visible("id:order")
            browser.wait_until_element_is_visible("id:receipt")
            break
        except:
            pass
    export_the_table_as_a_pdf(orders['Order number'])
    
    

def minimal_task():
    print("Done.")
    app = Application()
    excel = Files()
    library = Tables()
    http=HTTP()
    fil=http.download(order_file_url,overwrite=True)

    order_table = library.read_table_from_csv("orders.csv")
    error=False
    for order in order_table:
        try:
            if error:
                try:
                    fill_the_details(order)
                    browser.click_element_when_visible("id:order-another")
                    error=False
                except:
                    continue
            else:
                browser.click_element_when_visible(locator="//div[@class='alert-buttons']/button[contains(text(), 'OK')]")
                fill_the_details(order)
                browser.click_element_when_visible("id:order-another")
        except Exception as e:
            print(e)
            error=True
            continue
    return(order_table)

def read_secret():
    secrets = Secrets()
    name = secrets.get_secret("secrets")["Name"]
    print("Name : ",name)

def get_username():
    global username
    dialogs=Dialogs()
    dialogs.add_heading("Enter your Name")
    dialogs.add_text_input("username",label="What is your name?",placeholder="Give me some input here")
    result=dialogs.run_dialog()
    print(result)
    username=result["username"]
    return(username)

def success_dialog():
    dialogs=Dialogs()
    dialogs.add_heading("Your Orders have been processed")
    dialogs.add_text(username+" : all orders have been processed.")
    dialogs.run_dialog(title="Success")

if __name__ == "__main__":
    get_username()
    open_the_intranet_website()
    minimal_task()
    create_zip()
    read_secret()
    browser.close_browser()
    success_dialog()
    
