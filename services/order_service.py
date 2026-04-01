import sys
import os
import json
from services.mailservice import generar_html_reporte_creacion_ordenes, enviar_reporte_email
from datetime import datetime, timezone, timedelta
from clients.xorosoft_order_client import XorosoftOrderClient
from clients.mintsoft_order_client import MintsoftOrderClient
from mappers.order_mapper import map_xoro_order_to_mintsoft
from services.mailservice import generar_html_reporte_creacion_ordenes, enviar_reporte_email

#from loggers.order_logger import order_logger
from utils.datetime_util import iso_to_xorosoft, xorosoft_to_iso

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

FMT = "%m/%d/%Y %I:%M:%S %p"

STATE_DIR = os.path.join(ROOT, "state")
STATE_FILE = os.path.join(STATE_DIR, "sync_state.json")
os.makedirs(STATE_DIR, exist_ok=True)


class OrderSyncService:

    def __init__(self):
        self.xoro = XorosoftOrderClient()
        self.mint = MintsoftOrderClient()

    def _load_order_sync_state(self):
        if not os.path.exists(STATE_FILE):
            return {
                "orders": {
                    "created_at": None,
                    "updated_at": None
                }
            }

        with open(STATE_FILE, "r") as f:
            return json.load(f)

    def _save_order_sync_state(self, created_at=None):
        state = self._load_order_sync_state()
        state.setdefault("orders", {})

        if created_at:
            state["orders"]["created_at"] = created_at

        with open(STATE_FILE, "w") as f:
            json.dump(state, f, indent=4)

    def sync_all_orders(self):
        print("=== Sync ALL orders started ===")

        state = self._load_order_sync_state()
        created_iso = state["orders"].get("created_at")


        cutoff = datetime.now(timezone.utc).strftime(FMT)

        dt = datetime.strptime(cutoff, "%m/%d/%Y %I:%M:%S %p")
        offset = timezone(timedelta(hours=-4))
        dt_with_tz = dt.replace(tzinfo=offset)
        cutoff = dt_with_tz.isoformat()

        respuestas = []
        orders_o = []
        cargados_ok = []
        cargados_errores = []
        waves_pages = []
        for page in range(1,3):
            print(page)
            waves_pages.append(self.xoro.get_waves_since(
                page = page,
                created_at_min=created_iso,
                created_at_max=cutoff,
            ))
            print(waves_pages)
            if len(waves_pages[page-1].get("Data", {}).get("OrderData", [])) < page * 100:
                break
        #print("inicio", waves, "fin")
        for waves in waves_pages:
            order_list = waves.get("Data", {}).get("OrderData", [])
            wave_list = waves.get("Data", {}).get("WaveData", [])

            for i in range(len(order_list)):
                o_list = order_list[i]
                w_list = wave_list[i]
                num = o_list.get("OrderNumber")
                orders_o.append(num)
                mapped = map_xoro_order_to_mintsoft(o_list,w_list)
                carga = self.mint.create_order(mapped)
                if carga[0].get("Success") == True:
                    cargados_ok.append(num)
                else:
                    cargados_errores.append(num)
                print(carga)
                break
               
            #print(mapped)
            # cargar orden 

                               

            #Analizar este caso
        print(orders_o)  
        html_message = generar_html_reporte_creacion_ordenes(cargados_ok, cargados_errores)
        enviar_reporte_email(html_message, ["ngurfinkel@the5411.com", "bgallo@the5411.com" ], "Órdenes Holiday Xorosoft en Mintsoft")

        

        

        self._save_order_sync_state(
            created_at=cutoff,
        )

        return 
