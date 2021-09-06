import mechanicalsoup
import sys

class Option:
    def __init__(self,flag,value,desc):
        self.flag=flag
        self.value=value
        self.desc=desc

class SubCommand:
    def __init__(self,name,desc):
        self.desc = desc
        self.name = name
        self.options = []

    def addOption(self,option):
        self.options.append(option)

class ArgParser:
    def __init__(self):
        self.subcommands = []
        self.fields = []

    def addSubCommand(self, cmd):
        self.subcommands.append(cmd)

    def addField(self,name,required):
        self.fields.append(name)

    def parse(self,args):
        args.pop(0)
        parsedArgs = {}
        fieldCounter = 0
        # check for required fields
        for el in args:
            if("--" in el):
                sides = el.split("=")
                parsedArgs[sides[0].replace("--","")] = sides[1]
            else:
                parsedArgs[self.fields[fieldCounter]] = el
        return parsedArgs
            

    def __getSubCommandsString(self):
        subcmds = []
        for cmd in self.subcommands:
            subcmds.append(cmd.name)
        return "|".join(subcmds)

    def __getFieldsString(self):
        return "|".join(self.fields)
        
    def printHelp(self):
        print(f'fuzz [{self.__getSubCommandsString()}] {self.__getFieldsString()} OPTIONS')
        print(f'\nCOMMANDS:')
        for cmd in self.subcommands:
            print(f'\t{cmd.name} \t {cmd.desc}')
        print(f'\nOPTIONS:\n\tOptions can be given in any order.')
        for cmd in self.subcommands:
            print(f'\n\t{(cmd.name).upper()} options:')
            for option in cmd.options:
                print(f'\t  --{option.flag}={option.value}\t{option.desc}')
        
def main(args):
    browser = mechanicalsoup.StatefulBrowser()
    url = args["url"]
    browser.open(url+"/setup.php")
    browser.select_form()
    resp = browser.submit_selected()
    browser.follow_link("login")
    browser.select_form()
    browser["username"] = "admin"
    browser["password"] = "password"
    browser.submit_selected()
    print(browser.page)
    browser.follow_link("security")
    browser.select_form()
    browser["security"] = "low"

if __name__ == '__main__':
    #configure parser
    parser = ArgParser()
    parser.addField("url",True)

    discover = SubCommand("discover", "Output a comprehensive, human-readable list of all discovered inputs to the system. Techniques include both crawling and guessing.")
    discover.addOption(Option("common-words","file","Newline-delimited file of common words to be used in page guessing. Required."))
    discover.addOption(Option("extensions","file",'Newline-delimited file of path extensions, e.g. ".php". Optional. Defaults to ".php" and the empty string if not specified'))
    parser.addSubCommand(discover)

    test = SubCommand("test", "Discover all inputs, then attempt a list of exploit vectors on those inputs. Report anomalies that could be vulnerabilities.")
    test.addOption(Option("common-words","file","Newline-delimited file of common words to be used in page guessing. Required."))
    test.addOption(Option("extensions","file",'Newline-delimited file of path extensions, e.g. ".php". Optional. Defaults to ".php" and the empty string if not specified'))
    test.addOption(Option("vectors","file","Newline-delimited file of common exploits to vulnerabilities. Required."))
    test.addOption(Option("sanitized-chars","file",'Newline-delimited file of characters that should be sanitized from inputs. Defaults to just < and >'))
    test.addOption(Option("sensitive","file","Newline-delimited file data that should never be leaked. It's assumed that this data is in the application's database (e.g. test data), but is not reported in any response. Required."))
    test.addOption(Option("slow","500",'Number of milliseconds considered when a response is considered "slow". Optional. Default is 500 milliseconds'))
    parser.addSubCommand(test)

    main(parser.parse(sys.argv))