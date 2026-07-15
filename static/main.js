// Registro defensivo: en algunos casos el plugin no se auto-registra solo con el <script> tag.
if (typeof ChartZoom !== 'undefined') { Chart.register(ChartZoom); }

const btn = document.getElementById('btnAnalizar');
const errorEl = document.getElementById('error');
const resultadoEl = document.getElementById('resultado');
const campoAccession = document.getElementById('campoAccession');
const campoManual = document.getElementById('campoManual');

document.querySelectorAll('input[name="modo"]').forEach(radio => {
  radio.addEventListener('change', () => {
    const esAccession = radio.value === 'accession' && radio.checked;
    if (radio.checked) {
      campoAccession.style.display = esAccession ? 'block' : 'none';
      campoManual.style.display = esAccession ? 'none' : 'block';
    }
  });
});

btn.addEventListener('click', async () => {
  errorEl.style.display = 'none';
  resultadoEl.style.display = 'none';

  const modo = document.querySelector('input[name="modo"]:checked').value;
  let payload;

  if (modo === 'accession') {
    const accession = document.getElementById('accession').value.trim();
    if (!accession) {
      errorEl.textContent = 'Poné un accession de NCBI (ej: J01636).';
      errorEl.style.display = 'block';
      return;
    }
    payload = {accession};
  } else {
    const secuencia = document.getElementById('secuencia').value.trim();
    if (!secuencia) {
      errorEl.textContent = 'Pegá una secuencia antes de analizar.';
      errorEl.style.display = 'block';
      return;
    }
    payload = {secuencia};
  }

  btn.disabled = true;
  btn.textContent = 'Analizando…';

  try {
    const resp = await fetch('/analizar', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify(payload)
    });
    const data = await resp.json();

    if (data.error) {
      errorEl.textContent = data.error;
      errorEl.style.display = 'block';
    } else {
      renderResultado(data);
    }
  } catch (e) {
    errorEl.textContent = 'No se pudo conectar con el servidor.';
    errorEl.style.display = 'block';
  } finally {
    btn.disabled = false;
    btn.textContent = 'Analizar';
  }
});

let chartProb = null;

const btnAmpliar = document.getElementById('btnAmpliar');
const graficoContenedor = document.getElementById('graficoContenedor');
btnAmpliar.addEventListener('click', () => {
  graficoContenedor.classList.toggle('ampliado');
  const ampliado = graficoContenedor.classList.contains('ampliado');
  btnAmpliar.textContent = ampliado ? 'Achicar' : 'Ampliar';
  if (chartProb) chartProb.resize();
});

document.getElementById('btnResetZoom').addEventListener('click', () => {
  if (chartProb) chartProb.resetZoom();
});

function renderResultado(data) {
  const tira = document.getElementById('tira');
  tira.innerHTML = '';
  for (let i = 0; i < data.secuencia.length; i++) {
    const span = document.createElement('span');
    span.textContent = data.secuencia[i];
    span.className = data.camino_viterbi[i] === 'P' ? 'base-p' : 'base-b';
    tira.appendChild(span);
  }
  document.getElementById('scoreForward').textContent = data.score_forward.toFixed(2);
  document.getElementById('largoSecuencia').textContent = data.secuencia.length;
  document.getElementById('confianzaPromedio').textContent = (data.confianza_promedio * 100).toFixed(1) + '%';

  const posiciones = data.probabilidad_promotor.map((_, i) => i + 1);
  if (chartProb) {
    chartProb.data.labels = posiciones;
    chartProb.data.datasets[0].data = data.probabilidad_promotor;
    chartProb.data.datasets[1].data = data.gc_ventana;
    chartProb.resetZoom();
    chartProb.update();
  } else {
    chartProb = new Chart(document.getElementById('chartProb'), {
      type: 'line',
      data: {
        labels: posiciones,
        datasets: [
          {
            label: 'Probabilidad',
            data: data.probabilidad_promotor,
            borderColor: '#5EC8D8',
            backgroundColor: 'rgba(94,200,216,0.10)',
            borderWidth: 2,
            pointRadius: 0,
            pointHoverRadius: 4,
            fill: true,
            tension: 0.25
          },
          {
            label: '%GC',
            data: data.gc_ventana,
            borderColor: '#E8A33D',
            backgroundColor: 'transparent',
            borderWidth: 2,
            borderDash: [4, 3],
            pointRadius: 0,
            pointHoverRadius: 4,
            fill: false,
            tension: 0.25
          }
        ]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        interaction: { mode: 'index', intersect: false },
        plugins: {
          legend: { display: false },
          tooltip: {
            callbacks: {
              title: (items) => `Posición ${items[0].label}`
            }
          },
          zoom: {
            pan: { enabled: true, mode: 'x' },
            zoom: {
              wheel: { enabled: true },
              pinch: { enabled: true },
              drag: { enabled: false },
              mode: 'x'
            },
          }
        },
        scales: {
          y: { min: 0, max: 1, grid: { color: '#2A343E' }, ticks: { color: '#8A97A3' } },
          x: { grid: { display: false }, ticks: { color: '#8A97A3', maxTicksLimit: 20, autoSkip: true } }
        }
      }
    });
  }

  resultadoEl.style.display = 'block';
}