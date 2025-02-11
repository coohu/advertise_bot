"use client"
import Image from "next/image";
import { AcademicCapIcon } from '@heroicons/react/24/solid'
import Input from '@mui/joy/Input';
import Select from '@mui/joy/Select';
import Option from '@mui/joy/Option';
import DebounceInput from '@/compnents/DebouncedInput';
import FormControl from "@mui/joy/FormControl";
import FormLabel from "@mui/joy/FormLabel";
import Button from "@mui/joy/Button";
import Box from "@mui/joy/Box";
import { useEffect, useState } from "react";
import axios from "axios"
import CircularProgress from "@mui/joy/CircularProgress";
import LinearProgress from '@mui/joy/LinearProgress';
import Snackbar from '@mui/joy/Snackbar';

const Model = [
  {name:"Mistral AI",value:"mistral",id:0},
  {name:"通义千问2.5",value:"qwen2.5",id:1},
  {name:"羊驼2纯真版",value:"llama2-uncensored",id:2},
  {name:"羊驼3.2",value:"llama3.2",id:3},
  {name:"phi-4",value:"phi4",id:4},
  {name:"Gemma2",value:"gemma2",id:5},
  {name:"DeepSeek-r1",value:"deepseek-r1",id:6},
]
const url = 'http://localhost:8000'

export default function Home() {
  const [cfg, setCfg] = useState<any>({id:'',model: '', status: "none",brand: ""})
  const [prt, setPrt] = useState<string>('')
  const [msg, setMsg] = useState<string>('')
  const [msgs, setMsgs]= useState<any[]>([])
  const [error, setError] = useState<any>({value:false, msg:""})

  useEffect(() => {
    if(cfg.brand.length>0)
      localStorage.setItem("brand", cfg.brand)
    if(Model.find(it=>it.value==cfg.model))
      localStorage.setItem("model", cfg.model)
    if(cfg.id.length>0)
      localStorage.setItem("id", cfg.id)
  }, [cfg.brand, cfg.model, cfg.id])

  const handleSend =()=>{
    if(!msg.trim().length)
      return 
    
    setMsgs([...msgs, {'role': 'user','content': msg}])
    setCfg((r:any)=>{ return {...r, status:'type'}})
    let gen = true
    axios.post(`${url}/chat`, {id:cfg.id, query: msg}, {
      responseType: 'stream', 
      onDownloadProgress: (e:any) => {
        // console.log(e.event.currentTarget.responseText)
        // if(gen){
          //   setCfg((r:any)=>{ return {...r, status:'none'} })
          //   gen = false
          // }
          setPrt(e.event.currentTarget.responseText)
        }
      })
      .then((res:any) => {
        setPrt('')
        setMsgs(m=>[...m, {'role': 'assistant','content': res.data}])
      }).catch(e => {
        console.log('Stream error:---------------------', e);
        setError({value:true, msg:JSON.parse(e.response.data).detail })
      }).finally(()=>{
        setCfg((r:any)=>{ return {...r, status:'none'} })
      })
      setMsg('')
    }
    
  useEffect(()=>{
    const brand = localStorage.getItem("brand") || "大力水手饮料"
    const model = localStorage.getItem("model") || Model[3].value
    const id = localStorage.getItem("id") || ''
    console.log({id,model,brand})
    setup({id,model,brand})
  },[])
  
  const setup = (c:any) => {
    axios.post(`${url}/setup`, c).then((res:any)=>{
      if(res.data.code ==0){
        setCfg({...cfg, id:res.data.id, model:res.data.model, brand:res.data.brand})
      }else{
        setError({value:true, msg:res.data.msg })
      }
    })
    .catch(e=>{
      console.log(e)
      setError({value:true, msg:"网络错误！"})
    })
  }

  return (
    <div className="w-full h-screen flex flex-col justify-between pb-3">
      <header className="w-full flex flex-col gap-3 py-5">
        <div className="w-full flex items-center gap-3">
          <AcademicCapIcon className="size-8" />
          <h3 className="font-bold text-xl">广告Bot</h3>
        </div>
        <div className="flex items-center gap-20">
          <FormControl sx={{ width: "50%" }}>
            <FormLabel>输入产品或行业</FormLabel>
            <DebounceInput variant="soft" placeholder="输入产品或行业" sx={{ width: "100%" }} 
              value = {cfg.brand}
              debounceTimeout={2000}
              handleDebounce={(b:string)=>{
                if(b.length<1) return
                setup({...cfg, brand:b})
              }}
            />
          </FormControl>

          <FormControl sx={{ width: "50%" }}>
            <FormLabel >选择模型：</FormLabel>
            <Select variant="soft" value={cfg.model} sx={{ width: "100%" }} 
              onChange={(e:any,v:string|null)=>{
                if(!v && !Model.find(it=>it.value==v)) 
                  return
                setup({...cfg, model:v})
              }}
            >
            {Model.map((it:any)=> <Option value={it.value} key={it.value} >{it.name}</Option> )}
            </Select>
          </FormControl>
        </div>
      </header>
      <main className="w-full grow overflow-y-auto p-3 flex flex-col gap-3 justify-start bg-blue-50 rounded-lg">
        {msgs.map((it:any,id:number)=>
          <div className={it.role=='user'? "msgMe" : "msg"}   key={id}>
            {it.content}
          </div>
        )}
        {cfg.status == "type"?<div className="msg flex gap-3"   >
          <CircularProgress variant="outlined" size="sm"/>
          {/* <LinearProgress /> */}
          {prt}
        </div>:null}
      </main>
      <footer className="w-full bg-blue py-5">
        <Box display="flex" gap={1} alignItems="center" className="w-full">
          <Input placeholder="输入要求..."
            disabled={cfg.status!="none"}
            value={msg}
            onChange={(e) => setMsg(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === "Enter") handleSend(); 
            }}
            sx={{flexGrow: 1}}
          />

          <Button variant="solid"
            color="primary"
            onClick={handleSend}
            disabled={!msg.trim()||cfg.status!="none"}
          >发送
          </Button>
        </Box>
      </footer>
      <Snackbar anchorOrigin={{ 'vertical':'bottom', 'horizontal':'center' }}
        open={error.value} onClose={()=>setError({value:false, msg:""})} size ="lg" color="danger"variant="solid"
      > 
        {error.msg}
      </Snackbar>
    </div>
  );
}
