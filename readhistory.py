import os
import sqlite3 
import shutil
import atexit 
import datetime
import re 
import sys


CLEAN = "\033[32m[ CLEAN ✨]\033[0m"
NOTCLEAN = "\033[41m 💀 \033[0m"

def nano_to_time(timestamp_nanoseconds):
    timestamp_seconds = timestamp_nanoseconds / 10**9
    # Convert to a datetime object
    timestamp_datetime = datetime.datetime.fromtimestamp(timestamp_seconds)
    # Format the datetime object to display date and time in 12-hour AM/PM format
    return timestamp_datetime.strftime("%Y-%m-%d %I:%M:%S %p")

def edge_path():
    return f"C:\\Users\\{os.getlogin()}\\AppData\\Local\\Microsoft\\Edge\\User Data\\Default\\History"

def get_edge_db():
    shutil.copy(src=edge_path(), dst=os.path.join(os.getcwd(), "temp"))
    atexit.register(remove_edge_db)

def remove_edge_db():
    os.chdir(os.getcwd())
    try:os.remove(os.path.join(os.getcwd(), "temp"))
    except:pass

def read_edge_history():
    get_edge_db()
    connection = sqlite3.connect(os.path.join(os.getcwd(), "temp"))
    connection.text_factory = bytes  # Explicitly set text_factory to bytes
    cursor = connection.cursor()
    
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    table_names = [row[0] for row in cursor.fetchall()]
    all_table_data = {}
    
    for table_name in table_names:
        cursor.execute(f"SELECT * FROM {table_name.decode()};")
        table_data = cursor.fetchall()
        all_table_data[table_name] = table_data

    connection.close()
    return all_table_data

def read_edge_urls_table():
    get_edge_db()
    connection = sqlite3.connect(os.path.join(os.getcwd(), "temp"))
    connection.text_factory = bytes  # Explicitly set text_factory to bytes
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM urls;")
    urls_table_data = cursor.fetchall()
    connection.close()
    return urls_table_data

def delete_entry(database_path, table_name, condition_value):
    connection = sqlite3.connect(database_path)
    cursor = connection.cursor()

    # Delete the entry using the DELETE statement
    delete_query = f"DELETE FROM {table_name} WHERE id = ?;"
    cursor.execute(delete_query, (condition_value,))
    connection.commit()

    connection.close()

def delete_porn():
    urls = read_edge_urls_table()
    bad = []
    for item in urls:
        website = item[1].decode('utf-8')
        description = item[2].decode('utf-8')
        patterns = [r"xvideos\.com", r"pornhub\.com", r"xhamster\.com"]
        for pattern in patterns:
            matches = re.findall(pattern, website)
            if matches:
                bad.append(item[0])
                print(NOTCLEAN, website)
                break
            matches = re.findall(pattern, description)
            if matches:
                bad.append(item[0])
                print(NOTCLEAN, description)
                break
    connection = sqlite3.connect(edge_path())
    cursor = connection.cursor()
    for b in bad:
        delete_query = f"DELETE FROM urls WHERE id = ?;"
        cursor.execute(delete_query, (b,))
        connection.commit()
    connection.close()

        


def no_porn():
    urls = read_edge_urls_table()
    bad = []
    for item in urls:
        website = item[1].decode('utf-8')
        description = item[2].decode('utf-8')
        patterns = [re.compile(r"xvideos\.com"), re.compile(r"pornhub\.com"), re.compile(r"xhamster\.com")]
        for pattern in patterns:
            matches = re.findall(pattern, website)
            if matches:
                continue
            matches = re.findall(pattern, description)
            if matches:
                continue
            print(item[1].decode())
            print(item[2].decode())


def only_porn():
    urls = read_edge_urls_table()
    bad = []
    for item in urls:
        website = item[1].decode('utf-8')
        description = item[2].decode('utf-8')
        patterns = [re.compile(r"xvideos\.com"), re.compile(r"pornhub\.com"), re.compile(r"xhamster\.com")]
        for pattern in patterns:
            matches = re.findall(pattern, website)
            if matches:
                bad.append(item[0])
                print(NOTCLEAN, website)
                break
            matches = re.findall(pattern, description)
            if matches:
                bad.append(item[0])
                print(NOTCLEAN, description)
                break


def dump_history():
    urls = read_edge_urls_table()
    for item in urls:
        print("\nTime:        " + nano_to_time(item[5]) + "\nWebsite:     " + item[1].decode() + "\nDescription: " + item[2].decode())
        

def print_usage():
    print(f"""
edge       Edge Browser History Tool
  
    Usage:     {os.path.basename(__file__)} [options]
    
    Options:
          
          -p, --only-porn       Show only the porn.                 
          -x, --no-porn         Show none of the porn links.        
          -c, --clean           Remove only porn from the history.  👍
          -?, --where           Return the database directory.      
          -w, --remove-website  Remove any website with the address 
          -d, --data            Report my web history               
          delete                Delete the web history for good
          show                  Show the web history
          file                  Output to file
          tables                Show the types of data they keep tabs on
          all                   Show it all.
""")

def main():
    map = [
        "-p", "--only-porn",
        "-x", "--no-porn",
        "-c", "--clean",
        "-?", "--where",
        "-w", "--remove-website",
        "-d", "--data", 
    ]
    sys.argv.append(None)
    
    if sys.argv[1] == None:
        print_usage()
    
    if sys.argv[1]  in ["-p", "--only-porn"]:
        only_porn()
    elif sys.argv[1] in ["-x", "--no-porn"]:
        no_porn()
    elif sys.argv[1] in ["-c", "--clean"]:
        delete_porn()
    elif sys.argv[1] in ["-?", "--where"]:
        print(edge_path())
    elif sys.argv[1] in ["show"]:
        dump_history()
    elif sys.argv[1] in ["delete"]:
        os.remove(edge_path())
    elif sys.argv[1] in ["tables"]:
        get_edge_db()
        connection = sqlite3.connect(os.path.join(os.getcwd(), "temp"))
        connection.text_factory = bytes  # Explicitly set text_factory to bytes
        cursor = connection.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        table_names = [row[0] for row in cursor.fetchall()]
        print([x.decode() for x in table_names])
        connection.close()
    elif sys.argv[1] in ["file"]:
        try:
            file = sys.argv[2]
        except:
            file = "webhistory"
        with open(file, "rb") as f:
            x = read_edge_history()
            for name, items in x.items():
                f.write(name)
                for item in items:
                    f.write(b"\t"+item)
    if sys.argv[1] in ["all"]:
        from pprint import pprint
        pprint(read_edge_history())
        

    
       
main()