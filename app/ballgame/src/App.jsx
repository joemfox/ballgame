import { useState } from 'react'
import {
  ResizableHandle,
  ResizablePanel,
  ResizablePanelGroup,
} from "@/components/ui/resizable"

import Players from './components/Players.jsx'

function App() {
  return (
    <ResizablePanelGroup className="border" direction="horizontal">
      <ResizablePanel defaultSize={20}>One</ResizablePanel>
      <ResizableHandle />
      <ResizablePanel><Players/></ResizablePanel>
    </ResizablePanelGroup>
  )
}

export default App
