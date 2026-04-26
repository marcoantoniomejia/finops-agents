"""
Herramientas Extractivas de Compute Engine
==========================================
Scanners especializados en recorrer la red Compute del core de GCP para descubrir 
recursos sueltos o remanentes de destrucciones incompletas (ej. Máquinas borradas
sin demarcar el flag de borrar discos atados/boot o IPs reservadas que se apagaron).
"""

from google.cloud import compute_v1
import os

def find_orphaned_ips(project_id: str = None) -> list:
    """
    Lista las direcciones con status IN_USE falso. Cada una tiene su tarifa activa, 
    usualmente perjudicial o "pesada" a final del mes.
    """
    project_id = project_id or os.getenv("GOOGLE_CLOUD_PROJECT", "psa-infra-app-mx-dev-proj")
    client = compute_v1.AddressesClient()
    orphaned = []
    
    try:
        # Exploración en cascada regional / zonal.
        for region, scoped_list in client.aggregated_list(project=project_id):
            if scoped_list.addresses:
                for ip in scoped_list.addresses:
                    # Las direcciones de Forwarding o conectadas a LB tienen IN_USE.
                    if ip.status != "IN_USE" and ip.address_type == "EXTERNAL":
                        cost = 7.20  # Estimación genérica standard (~$0.01/hr) al mes de PISA
                        orphaned.append({
                            "project": project_id,
                            "type": "IP Externa (Orphan)",
                            "name": ip.name,
                            "ip": ip.address,
                            "region": region,
                            "cost_estimate_usd": cost,
                            "action": "LIBERAR MEDIANTE gcloud (A la espera de confirmación de dueños)"
                        })
    except Exception as e:
        print(f"[!] Imposible listar IPs reservadas para {project_id}: {e}")
        
    return orphaned

def find_unattached_disks(project_id: str = None) -> list:
    """
    Revisa Persistent Disks sueltos, que no se encuentran atados (users = null/empty) a 
    ninguna operación ni a máquinas que hagan lectura. Gastan lo mismo estén montados o no.
    """
    project_id = project_id or os.getenv("GOOGLE_CLOUD_PROJECT", "psa-infra-app-mx-dev-proj")
    client = compute_v1.DisksClient()
    orphaned = []
    
    try:
        for zone, scoped_list in client.aggregated_list(project=project_id):
            if scoped_list.disks:
                for d in scoped_list.disks:
                    # 'users' contiene la lista alfanumérica de VMs que utilizan el array del disco
                    if not d.users:  
                        gb = d.size_gb
                        cost = round(gb * 0.04, 2) # Costo Standard Persistent Disk. Referencial FinOps.
                        orphaned.append({
                            "project": project_id,
                            "type": "Disco Bloque no Anclado",
                            "name": d.name,
                            "zone": zone,
                            "size_gb": gb,
                            "cost_estimate_usd": cost,
                            "action": "EVALUAR_SNAPSHOT_Y_BORRAR"
                        })
    except Exception as e:
        print(f"[!] Fracaso recolectando Discos Persistentes en {project_id}: {e}")
        
    return orphaned
