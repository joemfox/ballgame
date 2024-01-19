import { useState } from 'react'
import {
  ResizableHandle,
  ResizablePanel,
  ResizablePanelGroup,
} from "@/components/ui/resizable"
import { ScrollArea } from "@/components/ui/scroll-area"
import { DndProvider } from 'react-dnd'
import { HTML5Backend } from 'react-dnd-html5-backend'

import Players from '@/components/Players.jsx'
import LineupCard from '@/components/Lineup.jsx'

export default function Team() {
  return (
    <DndProvider backend={HTML5Backend}>
    <ResizablePanelGroup className="border  max-h-screen" direction="horizontal">
      <ResizablePanel defaultSize={40}>
        <ScrollArea className="relative h-full">
        <LineupCard team={"TST"}/>
        </ScrollArea>
        </ResizablePanel>
      <ResizableHandle withHandle/>
      <ResizablePanel>
        <ScrollArea className="h-full">
        <Players/>
        </ScrollArea>
        </ResizablePanel>
    </ResizablePanelGroup>
    </DndProvider>
  )
}
