import { useState } from 'react'
import {
  ResizableHandle,
  ResizablePanel,
  ResizablePanelGroup,
} from "@/components/ui/resizable"
import { DndProvider } from 'react-dnd'
import { HTML5Backend } from 'react-dnd-html5-backend'

import Players from './components/Players.jsx'
import LineupCard from './components/Lineup.jsx'

function App() {
  return (
    <DndProvider backend={HTML5Backend}>
    <ResizablePanelGroup className="border" direction="horizontal">
      <ResizablePanel defaultSize={40}><LineupCard team={"TST"}/></ResizablePanel>
      <ResizableHandle />
      <ResizablePanel><Players/></ResizablePanel>
    </ResizablePanelGroup>
    </DndProvider>
  )
}

export const ItemTypes = {
  PLAYER: 'Player',
  'C':'C',
  '1B':'1B',
  '2B':'2B',
  '3B':'3B',
  'SS':'SS',
  'LF':'LF',
  'CF':'CF',
  'RF':'RF',
  'SP':'SP',
  'RP':'RP'
}

export default App
