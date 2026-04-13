// ==========================================
// 1. DATOS DE PRUEBA Y ESTADO
// ==========================================
const contenedoresMock = [
    { id: 101, lat: -1.66800, lon: -78.64500, llenado_porcentaje: 35, cap: 500 },
    { id: 102, lat: -1.67500, lon: -78.65000, llenado_porcentaje: 65, cap: 500 },
    { id: 103, lat: -1.66000, lon: -78.64000, llenado_porcentaje: 95, cap: 1000 },
    { id: 104, lat: -1.67100, lon: -78.64800, llenado_porcentaje: 20, cap: 500 },
    { id: 105, lat: -1.67300, lon: -78.65200, llenado_porcentaje: 85, cap: 1000 }
];

let mapaCiudadano = null;
let miUbicacion = { lat: -1.67098, lon: -78.64712 };
let rolPendienteLogin = 'ciudadano'; // Default

// ==========================================
// 2. NAVEGACIÓN, LOGIN Y REGISTRO
// ==========================================
function mostrarPanel(panelId) {
    // Ocultar todas las pantallas
    ['inicio', 'login', 'registro', 'ciudadano', 'conductor', 'admin'].forEach(id => {
        document.getElementById(`panel-${id}`).classList.add('d-none');
    });
    
    // Mostrar la solicitada
    document.getElementById(`panel-${panelId}`).classList.remove('d-none');
    
    // Controlar visibilidad del menú
    if(['inicio', 'login', 'registro'].includes(panelId)) {
        document.getElementById('contenedorBotonesAcceso').classList.remove('d-none');
        document.getElementById('btnCerrarSesion').classList.add('d-none');
    } else {
        document.getElementById('contenedorBotonesAcceso').classList.add('d-none');
        document.getElementById('btnCerrarSesion').classList.remove('d-none');
    }
}

// Preparar el formulario de Login
function prepararLogin(rol) {
    if(rol === 'admin' || rol === 'conductor' || rol === 'ciudadano') {
        rolPendienteLogin = rol;
    }
    
    let nombreRol = 'Ciudadano';
    if(rolPendienteLogin === 'conductor') nombreRol = 'Conductor';
    if(rolPendienteLogin === 'admin') nombreRol = 'Administrador';

    document.getElementById('tituloLogin').innerText = `Acceso ${nombreRol}`;
    mostrarPanel('login');
}

// Preparar el formulario de Registro
function prepararRegistro(rolSugerido) {
    // Los administradores no se registran a sí mismos
    if(rolSugerido === 'admin') rolSugerido = 'ciudadano'; 
    
    // Marcar el radio button correspondiente
    if(rolSugerido === 'conductor') {
        document.getElementById('regConductor').checked = true;
    } else {
        document.getElementById('regCiudadano').checked = true;
    }
    
    cambiarCamposRegistro(); // Actualizar UI de campos extra
    mostrarPanel('registro');
}

// Dinamismo del formulario de registro (Muestra/Oculta campos extra)
function cambiarCamposRegistro() {
    const rolSeleccionado = document.querySelector('input[name="tipoRegistro"]:checked').value;
    const titulo = document.getElementById('tituloCamposExtra');
    const divCiudadano = document.getElementById('camposCiudadano');
    const divConductor = document.getElementById('camposConductor');

    if (rolSeleccionado === 'conductor') {
        titulo.innerText = "Datos adicionales (Conductor)";
        divCiudadano.classList.add('d-none');
        divConductor.classList.remove('d-none');
    } else {
        titulo.innerText = "Datos adicionales (Ciudadano)";
        divConductor.classList.add('d-none');
        divCiudadano.classList.remove('d-none');
    }
}

// Simular creación de cuenta
function ejecutarRegistro(event) {
    event.preventDefault(); // Evitar que la página recargue
    const rolSeleccionado = document.querySelector('input[name="tipoRegistro"]:checked').value;
    
    alert(`¡Cuenta de ${rolSeleccionado} creada con éxito! Ya puedes iniciar sesión.`);
    prepararLogin(rolSeleccionado);
}

// Ejecutar Login
function ejecutarLogin(event) {
    event.preventDefault(); 
    mostrarPanel(rolPendienteLogin);
    if (rolPendienteLogin === 'ciudadano') iniciarFlujoCiudadano();
}

function cerrarSesion() {
    mostrarPanel('inicio');
}

// ==========================================
// 3. INTEGRACIÓN CON PYTHON (PERSONA 3)
// ==========================================
async function solicitarOptimizacionAPI() {
    const btn = document.getElementById('btnOptimizar');
    const divResultado = document.getElementById('resultadoIA');
    const lista = document.getElementById('listaRutaIA');
    const distancia = document.getElementById('distanciaIA');

    btn.innerHTML = `<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Procesando algoritmo...`;
    btn.disabled = true;

    try {
        const respuesta = await fetch('http://127.0.0.1:5000/api/optimizar', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                contenedores: contenedoresMock, 
                puntos_ilegales: [], 
                umbral: 70, 
                inicio_lat: -1.67098,
                inicio_lon: -78.64712
            })
        });

        const data = await respuesta.json();

        if(data.exito) {
            lista.innerHTML = '';
            data.data.ruta_ordenada.forEach((punto, index) => {
                const li = document.createElement('li');
                li.innerText = `Parada ${index + 1}: ${punto.id_punto} (Lat: ${punto.lat.toFixed(4)}, Lon: ${punto.lon.toFixed(4)})`;
                lista.appendChild(li);
            });
            distancia.innerText = data.data.distancia_total_km;
            divResultado.classList.remove('d-none');
        } else {
            alert("Error en el algoritmo: " + data.error);
        }

    } catch (error) {
        console.error(error);
        alert("🚨 Error de Conexión: Asegúrate de que el servidor Flask (app.py) esté corriendo en el puerto 5000.");
    } finally {
        btn.innerHTML = `Ejecutar Algoritmo de Rutas`;
        btn.disabled = false;
    }
}

// ==========================================
// 4. LÓGICA DEL MAPA (CIUDADANO)
// ==========================================
function iniciarFlujoCiudadano() {
    renderizarMapa();
}

function renderizarMapa() {
    if (mapaCiudadano) mapaCiudadano.remove();

    mapaCiudadano = L.map('mapa-ciudadano').setView([miUbicacion.lat, miUbicacion.lon], 15);
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png').addTo(mapaCiudadano);

    L.marker([miUbicacion.lat, miUbicacion.lon]).addTo(mapaCiudadano)
        .bindPopup("<b>📍 Estás aquí</b>").openPopup();

    procesarContenedores(contenedoresMock);
    setTimeout(() => { mapaCiudadano.invalidateSize(); }, 300);
}

function procesarContenedores(contenedores) {
    let masCercano = null, masVacio = null;
    let distMinima = Infinity, distMinimaVacio = Infinity;

    contenedores.forEach(c => {
        let distanciaKm = calcularDistancia(miUbicacion.lat, miUbicacion.lon, c.lat, c.lon);
        let colorHex = '#198754'; 
        
        if (c.llenado_porcentaje >= 80) colorHex = '#dc3545';
        else if (c.llenado_porcentaje >= 50) colorHex = '#fd7e14';

        L.circleMarker([c.lat, c.lon], { radius: 10, fillColor: colorHex, color: "#fff", weight: 2, fillOpacity: 0.9 })
            .addTo(mapaCiudadano).bindPopup(`<b>Contenedor #${c.id}</b><br>Llenado: ${c.llenado_porcentaje}%<br>Distancia: ${distanciaKm.toFixed(2)} km`);

        if (distanciaKm < distMinima) { distMinima = distanciaKm; masCercano = c; }
        if (c.llenado_porcentaje < 50 && distanciaKm < distMinimaVacio) { distMinimaVacio = distanciaKm; masVacio = c; }
    });

    if (masCercano) document.getElementById('info-mas-cercano').innerHTML = `ID #${masCercano.id} a ${distMinima.toFixed(2)} km`;
    if (masVacio) document.getElementById('info-mas-vacio').innerHTML = `ID #${masVacio.id} a ${distMinimaVacio.toFixed(2)} km`;
}

function calcularDistancia(lat1, lon1, lat2, lon2) {
    const R = 6371; 
    const dLat = (lat2 - lat1) * Math.PI / 180;
    const dLon = (lon2 - lon1) * Math.PI / 180;
    const a = Math.sin(dLat/2) * Math.sin(dLat/2) + Math.cos(lat1 * Math.PI / 180) * Math.cos(lat2 * Math.PI / 180) * Math.sin(dLon/2) * Math.sin(dLon/2);
    return R * 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1-a));
}