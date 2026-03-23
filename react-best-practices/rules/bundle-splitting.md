# Bundle optimization

## bundle-lazy-loading

### Why it matters
The browser has to download, parse, and compile your JavaScript before the page becomes interactive. If you import a 500KB chart library and a settings modal at the top of your file, users pay for that download even if they never see those components. `React.lazy()` (or `next/dynamic`) splits those components into separate chunks that load only when needed.

### ❌ Wrong — monolithic bundle
```jsx
import HugeChartLibrary from './HugeChartLibrary';
import ComplexSettingsModal from './ComplexSettingsModal';

function Dashboard() {
  const [showSettings, setShowSettings] = useState(false);

  return (
    <div>
      {/* User downloads both components on page load,
          even if they never open the settings modal */}
      <HugeChartLibrary />
      <button onClick={() => setShowSettings(true)}>Settings</button>
      {showSettings && <ComplexSettingsModal />}
    </div>
  );
}
```

### ✅ Right — split and load on demand
```jsx
// These files aren't downloaded until the component is rendered
const HugeChartLibrary = React.lazy(() => import('./HugeChartLibrary'));
const ComplexSettingsModal = React.lazy(() => import('./ComplexSettingsModal'));

function Dashboard() {
  const [showSettings, setShowSettings] = useState(false);

  return (
    <div>
      <Suspense fallback={<SkeletonChart />}>
        <HugeChartLibrary />
      </Suspense>

      <button onClick={() => setShowSettings(true)}>Settings</button>
      
      {showSettings && (
        <Suspense fallback={<Spinner />}>
          <ComplexSettingsModal />
        </Suspense>
      )}
    </div>
  );
}
```

---

## bundle-tree-shaking-barrel

### Why it matters
Barrel files (`index.js` files that re-export everything from a folder) can prevent bundlers from tree-shaking. If you import one small button from a barrel that re-exports 5,000 components, the bundler may pull in all of them.

### ❌ Wrong — barrel import
```jsx
// Webpack may pull in every component in the ui/ folder
import { Button, Checkbox, HugeDatePicker } from '@/components/ui';
```

### ✅ Right — direct imports
```jsx
// Only imports the code you actually use
import Button from '@/components/ui/Button';
import Checkbox from '@/components/ui/Checkbox';
import HugeDatePicker from '@/components/ui/HugeDatePicker';
```

---
**Related rules:** `async-suspense-boundaries`
