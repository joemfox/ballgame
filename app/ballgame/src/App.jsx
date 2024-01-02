import { useState } from 'react'
import {
  ResizableHandle,
  ResizablePanel,
  ResizablePanelGroup,
} from "@/components/ui/resizable"

import Players from './components/Players.jsx'

function App() {
  const [count, setCount] = useState(0)

  return (
    <ResizablePanelGroup className="max-w-xl border" direction="horizontal">
      <ResizablePanel>One</ResizablePanel>
      <ResizableHandle />
      <ResizablePanel><Players/></ResizablePanel>
    </ResizablePanelGroup>
  )
}

export default App
