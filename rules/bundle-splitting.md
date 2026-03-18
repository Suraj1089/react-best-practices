# Bundle Optimization

## bundle-lazy-loading

### Why it matters
Shipping massive megabytes of JavaScript natively forces the browser to aggressively download, parse, and deeply compile scripts completely before the page conceptually becomes interactive. `React.lazy()` (or `next/dynamic`) functionally chunks your bundle strictly into smaller independent payloads, natively deferring the deeply heavy structural code until the explicit exact moment the user structurally interacts with or views that specific component.

### ❌ Wrong — monolithic bundle
```jsx
import HugeChartLibrary from './HugeChartLibrary';
import ComplexSettingsModal from './ComplexSettingsModal';

function Dashboard() {
  const [showSettings, setShowSettings] = useState(false);

  return (
    <div>
      {/* 🚨 User pays the 500KB download penalty for HugeChartLibrary and 
          ComplexSettingsModal instantly on page load, even if they never open them! */}
      <HugeChartLibrary />
      <button onClick={() => setShowSettings(true)}>Settings</button>
      {showSettings && <ComplexSettingsModal />}
    </div>
  );
}
```

### ✅ Right — split and dynamically load
```jsx
// 🛠️ The browser literally doesn't download these files until natively requested
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
"Barrel files" (`index.js` files that blindly export dozens of other files) forcefully trick bundlers structurally into eagerly explicitly importing fundamentally massive amounts of unused code natively into the final client payload. If a component imports one tiny SVG icon from a barrel aggressively exporting 5,000 icons, it frequently fundamentally compiles identically all 5,000 icons.

### ❌ Wrong — barrel import
```jsx
// 🚨 Next.js/Webpack may spectacularly fail to tree-shake this, 
// pulling in every single component identically in the entire ui/ folder
import { Button, Checkbox, HugeDatePicker } from '@/components/ui';
```

### ✅ Right — deep structurally direct imports
```jsx
// 🛠️ Mathematically guaranteed explicitly to strictly import uniquely the target code
import Button from '@/components/ui/Button';
import Checkbox from '@/components/ui/Checkbox';
import HugeDatePicker from '@/components/ui/HugeDatePicker';
```

---
**Related rules:** `async-suspense-boundaries`
