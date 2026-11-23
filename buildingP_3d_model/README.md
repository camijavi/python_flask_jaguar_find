# Edificio P — Prototipo 3D / Isométrico (Archivado)

Esta carpeta conserva fuera de `frontend/` los archivos originales del prototipo 3D (Three.js WebGL) y del modal isométrico SVG creados inicialmente solo para el **Edificio P (Copérnico)**.

## Archivos archivados

- `buildingP.html`: Visor 3D/2.5D en Three.js WebGL (4,777 líneas) con arquitectura manual para los 5 pisos del Edificio P.
- `buildingPIsometricModal.html`: Versión anterior en modal SVG isométrico del Edificio P.
- `buildingPIsometric.js`: Controlador cliente del modal isométrico anterior.
- `buildingPIsometric.css`: Estilos del modal isométrico anterior.

## Estado en la aplicación activa

La aplicación realiza toda la navegación peatonal directamente en el **Mapa 2D/2.5D del Campus** con instrucciones humanas paso a paso (incluyendo pisos, escaleras, rampas y salones internos) calculadas por el **Grafo Ponderado, Dirigido y No Completo** $G = (V, E, W)$ y los **18 subgrafos internos** en `backend/subgraphs/`, sin abrir una vista modal aparte por edificio.
