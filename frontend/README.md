# AI Repo Evaluator - Frontend

Frontend del asistente de evaluación de repositorios con IA para el bootcamp de IA.

## 🚀 Tecnologías

- **[Next.js 14](https://nextjs.org/)** - Framework React con App Router
- **[TypeScript](https://www.typescriptlang.org/)** - JavaScript tipado
- **[Tailwind CSS](https://tailwindcss.com/)** - Framework CSS utility-first
- **[Axios](https://axios-http.com/)** - Cliente HTTP
- **[Lucide React](https://lucide.dev/)** - Iconos
- **[Recharts](https://recharts.org/)** - Gráficos

## 📁 Estructura del Proyecto

```
frontend/
├── app/                    # App Router de Next.js
│   ├── layout.tsx         # Layout principal
│   ├── page.tsx           # Página de inicio
│   └── globals.css        # Estilos globales
├── components/            # Componentes React
│   ├── ui/               # Componentes UI reutilizables
│   ├── layout/           # Componentes de layout (Header, Footer, etc.)
│   └── forms/            # Componentes de formularios
├── lib/                  # Utilidades y configuraciones
│   ├── api/             # Cliente API y endpoints
│   └── utils/           # Funciones de utilidad
├── types/               # Tipos TypeScript compartidos
├── hooks/               # Custom React Hooks
├── public/              # Archivos estáticos
└── .env.local          # Variables de entorno (no commitear)
```

## 🛠️ Instalación

### Prerequisitos

- Node.js 20.x LTS
- npm 10.x

### Pasos

1. **Instalar dependencias**
   ```bash
   npm install
   ```

2. **Configurar variables de entorno**
   ```bash
   cp .env.example .env.local
   ```
   Editar `.env.local` con tus valores:
   ```env
   NEXT_PUBLIC_API_URL=http://localhost:8000
   ```

3. **Ejecutar en modo desarrollo**
   ```bash
   npm run dev
   ```
   La aplicación estará disponible en [http://localhost:3000](http://localhost:3000)

## 📜 Scripts Disponibles

```bash
npm run dev      # Ejecuta el servidor de desarrollo
npm run build    # Construye la aplicación para producción
npm run start    # Inicia el servidor de producción
npm run lint     # Ejecuta el linter
```

## 🔌 Integración con Backend

El frontend se comunica con el backend FastAPI mediante Axios.

- **URL Base**: Configurada en `NEXT_PUBLIC_API_URL`
- **Cliente API**: `lib/api/client.ts`

### Endpoints principales (ejemplo)

```typescript
import apiClient from '@/lib/api/client';

// Obtener rúbricas
const rubrics = await apiClient.get('/api/rubrics');

// Evaluar repositorio
const evaluation = await apiClient.post('/api/evaluate', {
  rubricId,
  repositoryUrl,
  // ...
});
```

## 🎨 Estilos con Tailwind CSS

Usa las clases de Tailwind directamente en los componentes:

```tsx
<div className="bg-blue-500 text-white p-4 rounded-lg">
  ¡Hola mundo!
</div>
```

Para estilos condicionales, usa la utilidad `cn`:

```tsx
import { cn } from '@/lib/utils/cn';

<div className={cn(
  'base-styles',
  isActive && 'active-styles',
  className
)}>
  Contenido
</div>
```

## 📊 Uso de Recharts

Ejemplo de gráfico simple:

```tsx
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip } from 'recharts';

const data = [
  { name: 'Criterio 1', score: 80 },
  { name: 'Criterio 2', score: 95 },
];

<BarChart width={500} height={300} data={data}>
  <CartesianGrid strokeDasharray="3 3" />
  <XAxis dataKey="name" />
  <YAxis />
  <Tooltip />
  <Bar dataKey="score" fill="#8884d8" />
</BarChart>
```

## 🔧 Desarrollo

### Crear un nuevo componente

```bash
# Componente UI
touch components/ui/Button.tsx

# Componente de formulario
touch components/forms/EvaluationForm.tsx
```

### Añadir tipos TypeScript

Edita `types/index.ts` para añadir nuevos tipos compartidos.

### Custom Hooks

Crea hooks personalizados en la carpeta `hooks/`:

```typescript
// hooks/useEvaluation.ts
export function useEvaluation() {
  // Tu lógica aquí
}
```

## 🐳 Docker

El Dockerfile será creado y gestionado por el equipo de backend.

Configuración esperada:
- **Puerto**: 3000
- **Imagen base**: `node:20-slim`

## 📝 Notas

- Las variables de entorno deben tener el prefijo `NEXT_PUBLIC_` para estar disponibles en el cliente
- No commitear `.env.local` al repositorio (ya está en `.gitignore`)
- Usar TypeScript para todos los componentes nuevos

## 🤝 Contribución

1. Crear rama desde `develop`
2. Hacer cambios
3. Commitear siguiendo conventional commits
4. Hacer pull request

## 📧 Contacto

**Stakeholder**: David Robert - david.robert@gmail.com
