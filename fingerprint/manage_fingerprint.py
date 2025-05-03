import threading
from pyzkfp import ZKFP2

def capture_fingerprint(zkfp2, label, popup, db, regis_id, on_success):
    def run():
        zkfp2.Init()
        zkfp2.OpenDevice(0)
        template = []

        for i in range(3):
            while True:
                capture = zkfp2.AcquireFingerprint()
                if capture:
                    tmp, img = capture
                    template.append(tmp)

                    label.after(0, lambda i=i: label.configure(
                        text=f"{i + 1}", font=('TH SarabunPSK', 56, 'bold')
                    ))
                    break

        regTemp, regTempLen = zkfp2.DBMerge(*template)
        result = db.set_fingerprint(regis_id, bytes(regTemp))

        if result:
            popup.after(0, lambda: (
                on_success(),
                popup.destroy()
            ))

    threading.Thread(target=run, daemon=True).start()

def get_fingerprint_from_zk():
    def run():
        zkfp2 = ZKFP2()
        zkfp2.Init()
        zkfp2.OpenDevice(0)
        while True:
            capture = zkfp2.AcquireFingerprint()
            print('รอจับภาพนิ้วมือ')
            if capture:
                tmp, img = capture
                print('in if capture')
                break
        return tmp
            
    threading.Thread(target=run,daemon=True).start()
    return 

        
    
