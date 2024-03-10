import { useEffect, useState } from 'react'

import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import axios from 'axios'

import { ScrollArea } from "@/components/ui/scroll-area"


import StatlineTable from '@/components/StatlineTable.jsx'

export default function Team() {




  return (
        <ScrollArea className="h-full">
        <Tabs defaultValue="hit" className="">
          <TabsList>
            <TabsTrigger value="hit">Hitters</TabsTrigger>
            <TabsTrigger value="pitch">Pitchers</TabsTrigger>
          </TabsList>
          <TabsContent value="hit">
        <StatlineTable
          type="hit"
          scoreType="FAN"
         />
         </TabsContent>
         <TabsContent value="pitch">
        <StatlineTable
          type="pitch"
          scoreType="FAN"
         />
         </TabsContent>
         </Tabs>
        </ScrollArea>

  )
}
