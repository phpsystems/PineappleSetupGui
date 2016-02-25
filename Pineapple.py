#!/usr/bin/python

from Tkinter import *
from subprocess import *
import getnifs
import ttk
import os


# Frame Setup
root= Tk()
root.title("Wifi Pineapple Network Setup")

pineapple="172.16.42.42"
pineint=""
gw=""
mask="255.255.255.0"
interint=""
resetIptables=""
b1=""
b2=""
b3=""
c=""

def pineintfun(val):
	global pineint, pineapple, b1 
	pineint = val.widget.get()
	# Set pineapple to the ip address of the interface.
	interfaces = getnifs.get_network_interfaces()
	for i in interfaces:
		if i.name == pineint:
			pineapple="172.16.42.42"
			try:
				if i.addresses[2] is not None:
					pineapple = i.addresses[2]
	
			except:
				pass
			
			b1.delete(0, END)
			b1.insert(0, pineapple)
			

def interintfun(val):
	global interint
	interint = val.widget.get()

	
def setupNetworking():

	global pineint, interint, pineapple, gw, mask, resetIptables, root
	pineapple = b1.get()
	gw = b2.get()
	mask = b3.get()
	pinenet = "%s/%s" % (pineapple, mask)

	# Forwarding set up
	forwarding = "/sbin/sysctl -q -w net.ipv4.ip_forward=1"
	call (forwarding, shell=True)

	# Zero IPtables?

	if resetIptables.get():
		reset = "iptables -X"
		call (reset, shell=True)
		reset = "iptables -F"
		call (reset, shell=True)


	# Assign Rules
	command = "	ifconfig %s %s netmask %s up " % (pineint, pineapple, mask)
	call (command, shell=True)
	command = "iptables -A FORWARD -i %s -o %s -s %s/%s -m state --state NEW -j ACCEPT" % (interint, pineint, pineapple, mask) 
	call (command, shell=True)
	command = "iptables -A FORWARD -m state --state ESTABLISHED,RELATED -j ACCEPT"
	call (command, shell=True)
	command = "iptables -A POSTROUTING -t nat -j MASQUERADE"
	call (command, shell=True)
	command = "route del default"
	call (command, shell=True)
	command = "route add default gw %s" % (gw)
	call (command, shell=True)

	print "Networking Setup."
	root.destroy()
	exit

def main():

	if os.geteuid() != 0:
		exit("You need to have root privileges to run this script.\nPlease try again, this time using 'sudo'. Exiting.")

	global b1,b2,b3,c,resetIptables,root


	logo = PhotoImage(file="pineapple.png")

	desc = """
	Wifi Pineapple Set up utility 
	"""

	w1 = Label(root,image=logo).pack(side="left")

	w2 = Label(root, justify=LEFT, padx=10, text=desc).pack()

	w3 = Label(root, justify=LEFT, padx=10, text="""Choose the Pineapple Interface:""").pack()

	interfaces = getnifs.get_network_interfaces()
	interfacelist = [i.name for i in interfaces]

	int1select = ttk.Combobox(root, values=interfacelist)
	int1select.bind("<<ComboboxSelected>>", pineintfun)
	int1select.pack()

	w3 = Label(root, justify=LEFT, padx=10, text="""Choose the internet Interface:""").pack()
	int2select = ttk.Combobox(root, values=interfacelist)
	int2select.bind("<<ComboboxSelected>>", interintfun)
	int2select.pack()
	
	# Reset IPTables CheckBox
	resetIptables = IntVar()
	c = Checkbutton(root, text="Reset Firewall?", variable=resetIptables, onvalue=1, offvalue=0)
	c.pack()

	t1 = Label(root, justify=LEFT, padx=10, text="""IP of Pineapple Interface:""").pack()
	# IP Address boxes for the IP Address.
	b1 = Entry(root, width=16, textvariable=pineapple)
	b1.pack()
	b1.insert(0, pineapple)

	t3 = Label(root, justify=LEFT, padx=10, text="""NetMask:""").pack()
	# Netmask
	b3 = Entry(root, width=16, textvariable=mask)
	b3.pack()
	b3.insert(0, mask)

	t2 = Label(root, justify=LEFT, padx=10, text="""Default Gateway:""").pack()
	# Default Gateway
	b2 = Entry(root, width=16, textvariable=gw)
	b2.pack()
	b2.insert(0, gw)

	# Setup Networking
	button1 = Button(root,text='Set Up Networking', width=25, command=setupNetworking)
	button1.pack(side="left")


	# Exit control
	button2 = Button(root,text='Exit', width=25, command=root.destroy)
	button2.pack(side="left")

	root.mainloop()

if __name__ == "__main__":
	main()
