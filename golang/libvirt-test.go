package main

import (
	"bytes"
	"encoding/json"
	"encoding/xml"
	"fmt"
	libvirt "github.com/libvirt/libvirt-go"
	"github.com/mostlygeek/arp"
)

func pingHost(host string) {
	cmd := exec.Command("ping", "-c", "1", host)
	cmd.Run()
}

func getArpTable() map[string]string {
	arp_init := arp.Table()
	arp_table := make(map[string]string, len(arp_init))

	for k, v := range arp_init {
		arp_table[v] = k
	}

	return arp_table
}

func main() {
	conn, err := libvirt.NewConnect("qemu:///system")
	if err != nil {
		panic(err)
	}
	defer conn.Close()

	doms, err := conn.ListAllDomains(libvirt.CONNECT_LIST_DOMAINS_ACTIVE)
	if err != nil {
		panic(err)
	}

	macs := make(map[string]string, len(doms))
	arp_table := getArpTable()

	for _, dom := range doms {
		name, err := dom.GetName()
		if err != nil {
			continue
		}

		xmlval, err := dom.GetXMLDesc(0)
		if err != nil {
			continue
		}

		decoder := xml.NewDecoder(bytes.NewReader([]byte(xmlval)))
		for {
			t, _ := decoder.Token()
			if t == nil {
				break
			}

			switch se := t.(type) {
			case xml.StartElement:
				if se.Name.Local == "mac" {
					for _, attr := range se.Attr {
						if attr.Name.Local == "address" {
							ip := arp_table[attr.Value]
							macs[ip] = name
						}
					}
				}
			}

		}

		dom.Free()
	}

	out, _ := json.Marshal(macs)
	fmt.Println(string(out))
}
