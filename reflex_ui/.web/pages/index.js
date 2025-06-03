/** @jsxImportSource @emotion/react */


import { Fragment, useCallback, useContext, useRef } from "react"
import { Box as RadixThemesBox, Flex as RadixThemesFlex, Text as RadixThemesText } from "@radix-ui/themes"
import { EventLoopContext, StateContexts } from "$/utils/context"
import { Event, getRefValue, getRefValues, isTrue, refs } from "$/utils/state"
import { BoxSelectIcon as LucideBoxSelectIcon, Info as LucideInfo, LoaderCircle as LucideLoaderCircle, Plus as LucidePlus, SendHorizontal as LucideSendHorizontal, SquareM as LucideSquareM, Trash2 as LucideTrash2, X as LucideX } from "lucide-react"
import {  } from "react-dropzone"
import { useDropzone } from "react-dropzone"
import NextHead from "next/head"
import { jsx } from "@emotion/react"



export function Textarea_84b6d82b1dc0bca178b53ddf41f472e3 () {
  
  const reflex___state____state__app___states___chat_state____chat_state = useContext(StateContexts.reflex___state____state__app___states___chat_state____chat_state)
  const [addEvents, connectErrors] = useContext(EventLoopContext);


  const on_change_aa5a2e1592dd1fff977dc2c159fdf7e9 = useCallback(((_e) => (addEvents([(Event("reflex___state____state.app___states___chat_state____chat_state.set_input_message", ({ ["value"] : _e["target"]["value"] }), ({  })))], [_e], ({  })))), [addEvents, Event])



  
  return (
    jsx("textarea",{className:"flex-grow p-3 bg-white border border-slate-300 rounded-xl resize-none focus:outline-none focus:ring-2 focus:ring-sky-400 min-h-[60px] max-h-40 text-slate-800 placeholder-slate-400 text-sm",defaultValue:reflex___state____state__app___states___chat_state____chat_state.input_message,onChange:on_change_aa5a2e1592dd1fff977dc2c159fdf7e9,placeholder:"Ask Vino AI..."},)

  )
}

export function Fragment_bcd124deb6d2681000ab043dd8b19699 () {
  
  const reflex___state____state__app___states___chat_state____chat_state = useContext(StateContexts.reflex___state____state__app___states___chat_state____chat_state)





  
  return (
    jsx(
Fragment,
{},
(reflex___state____state__app___states___chat_state____chat_state.processing ? (jsx(
Fragment,
{},
jsx(LucideLoaderCircle,{className:"animate-spin",size:20},)
,)) : (jsx(
Fragment,
{},
jsx(LucideSendHorizontal,{size:20},)
,))),)
  )
}

export function Button_5f7ccc43ae828ceeb27bd9f2e5992846 () {
  
  const [addEvents, connectErrors] = useContext(EventLoopContext);


  const on_click_b3c5af4eb74fb5b59982e7c582f6bed0 = useCallback(((...args) => (addEvents([(Event("reflex___state____state.app___states___chat_state____chat_state.clear_uploaded_file", ({  }), ({  })))], args, ({  })))), [addEvents, Event])



  
  return (
    jsx(
"button",
{className:"p-1 rounded hover:bg-slate-200",onClick:on_click_b3c5af4eb74fb5b59982e7c582f6bed0,type:"button"},
jsx(LucideX,{className:"text-slate-500 hover:text-red-500",size:12},)
,)
  )
}

export function Fragment_de5178b50191bc21ea6c5a3095ef5e52 () {
  
  const reflex___state____state__app___states___chat_state____chat_state = useContext(StateContexts.reflex___state____state__app___states___chat_state____chat_state)





  
  return (
    jsx(
Fragment,
{},
(!((reflex___state____state__app___states___chat_state____chat_state.uploaded_file_name === "")) ? (jsx(
Fragment,
{},
jsx(
"div",
{className:"flex items-center justify-between gap-2 px-4 mt-2 py-1 bg-slate-100 border border-slate-200 rounded-md text-xs"},
jsx(Span_581409b9e7c121e0916742be9eb8cd6b,{},)
,jsx(Button_5f7ccc43ae828ceeb27bd9f2e5992846,{},)
,),)) : (jsx(Fragment,{},)
)),)
  )
}

export function Button_e04019c807f87144548760b6374cdbfd () {
  
  const reflex___state____state__app___states___chat_state____chat_state = useContext(StateContexts.reflex___state____state__app___states___chat_state____chat_state)
  const [addEvents, connectErrors] = useContext(EventLoopContext);


  const on_click_388916257efaf69450afe21794004976 = useCallback(((...args) => (addEvents([(Event("reflex___state____state.app___states___chat_state____chat_state.toggle_tasks", ({  }), ({  })))], args, ({  })))), [addEvents, Event])



  
  return (
    jsx(
"button",
{className:(reflex___state____state__app___states___chat_state____chat_state.tasks_active ? "px-3 py-2 text-sm font-medium text-white bg-sky-500 border border-sky-500 rounded-lg hover:bg-sky-600 flex items-center transition-colors" : "px-3 py-2 text-sm font-medium text-slate-700 bg-white border border-slate-300 rounded-lg hover:bg-slate-100 flex items-center transition-colors"),onClick:on_click_388916257efaf69450afe21794004976},
jsx(LucideSquareM,{className:"mr-1.5",size:16},)
,"Tasks"
,)
  )
}

export function Button_6e75cf5bec94bc944097a17812febadd () {
  
  const reflex___state____state__app___states___chat_state____chat_state = useContext(StateContexts.reflex___state____state__app___states___chat_state____chat_state)
  const [addEvents, connectErrors] = useContext(EventLoopContext);


  const on_click_8a11f42b64a1ce23abecf7ded7fa75ef = useCallback(((...args) => (addEvents([(Event("reflex___state____state.app___states___chat_state____chat_state.toggle_explain", ({  }), ({  })))], args, ({  })))), [addEvents, Event])



  
  return (
    jsx(
"button",
{className:(reflex___state____state__app___states___chat_state____chat_state.explain_active ? "px-3 py-2 text-sm font-medium text-white bg-sky-500 border border-sky-500 rounded-lg hover:bg-sky-600 flex items-center transition-colors" : "px-3 py-2 text-sm font-medium text-slate-700 bg-white border border-slate-300 rounded-lg hover:bg-slate-100 flex items-center transition-colors"),onClick:on_click_8a11f42b64a1ce23abecf7ded7fa75ef},
jsx(LucideInfo,{className:"mr-1.5",size:16},)
,"Explain"
,)
  )
}

export function Flex_f9bc6248d62c14ee3f4923ca1ef51d25 () {
  
  const reflex___state____state__app___states___chat_state____chat_state = useContext(StateContexts.reflex___state____state__app___states___chat_state____chat_state)





  
  return (
    jsx(
RadixThemesFlex,
{align:"start",className:"rx-Stack",css:({ ["alignItems"] : "stretch", ["padding"] : "1rem", ["width"] : "100%", ["flexGrow"] : "1", ["overflowY"] : "auto" }),direction:"column",gap:"1"},
reflex___state____state__app___states___chat_state____chat_state.messages.map((message,index_b058de3ad0f07462)=>(jsx(
RadixThemesBox,
{css:({ ["alignSelf"] : (message["is_ai"] ? "start" : "end"), ["background"] : (message["is_ai"] ? "gray.100" : "blue.100"), ["padding"] : "0.5rem", ["borderRadius"] : "lg", ["maxWidth"] : "70%" }),key:index_b058de3ad0f07462},
jsx(
RadixThemesText,
{as:"p"},
message["text"]
,),))),)
  )
}

export function Div_6fcc06680e956e9456738a77d44d26ce () {
  
  const reflex___state____state__app___states___chat_state____chat_state = useContext(StateContexts.reflex___state____state__app___states___chat_state____chat_state)
  const [addEvents, connectErrors] = useContext(EventLoopContext);





  
  return (
    jsx(
"div",
{className:"flex flex-wrap items-center gap-x-4 gap-y-2"},
reflex___state____state__app___states___chat_state____chat_state.alignment_options.map((option,index_dee09f99185ddaab)=>(jsx(
"label",
{className:"flex items-center cursor-pointer",key:index_dee09f99185ddaab},
jsx("input",{checked:(reflex___state____state__app___states___chat_state____chat_state.selected_alignment === option),className:"mr-1.5 accent-sky-500",defaultValue:option,name:"alignment_option",onChange:((_e) => (addEvents([(Event("reflex___state____state.app___states___chat_state____chat_state.set_selected_alignment", ({ ["alignment"] : option }), ({  })))], [_e], ({  })))),type:"radio"},)
,jsx(
"span",
{className:"text-sm text-slate-700 font-medium"},
option
,),))),)
  )
}

export function Comp_548621951a4f97ca805bc5a5102f0d51 () {
  
  const ref_chat_file_upload = useRef(null); refs["ref_chat_file_upload"] = ref_chat_file_upload;
  const [addEvents, connectErrors] = useContext(EventLoopContext);
  const on_drop_c761e72ff168a04e764418aa8b1588cf = useCallback(((_files) => (addEvents([(Event("reflex___state____state.app___states___chat_state____chat_state.handle_upload", ({ ["files"] : _files, ["upload_id"] : "chat_file_upload" }), ({  }), "uploadFiles"))], [_files], ({  })))), [addEvents, Event])
  const { getRootProps: vbsvjfmc, getInputProps: deoxzitv, isDragActive: erqbkbgg} = useDropzone(({ ["onDrop"] : on_drop_c761e72ff168a04e764418aa8b1588cf, ["multiple"] : true, ["id"] : "chat_file_upload" }));





  
  return (
    jsx(
Fragment,
{},
jsx(
RadixThemesBox,
{className:"rx-Upload flex-shrink-0",id:"chat_file_upload",ref:ref_chat_file_upload,...vbsvjfmc()},
jsx("input",{type:"file",...deoxzitv()},)
,jsx(
"div",
{className:"p-2.5 rounded-lg border border-slate-300 hover:border-sky-400 cursor-pointer group flex items-center justify-center bg-white hover:bg-slate-50"},
jsx(LucidePlus,{className:"text-slate-600 group-hover:text-sky-500 transition-colors",size:18},)
,),),)
  )
}

export function Span_581409b9e7c121e0916742be9eb8cd6b () {
  
  const reflex___state____state__app___states___chat_state____chat_state = useContext(StateContexts.reflex___state____state__app___states___chat_state____chat_state)





  
  return (
    jsx(
"span",
{className:"text-xs text-slate-600"},
("File: "+reflex___state____state__app___states___chat_state____chat_state.uploaded_file_name)
,)
  )
}

export function Button_0ec4ddd6b671297f79d185e4a7d65d33 () {
  
  const [addEvents, connectErrors] = useContext(EventLoopContext);


  const on_click_7e7f04377e8df047cd26e059a1123541 = useCallback(((...args) => (addEvents([(Event("reflex___state____state.app___states___chat_state____chat_state.toggle_prompt_toolbox", ({  }), ({  })))], args, ({  })))), [addEvents, Event])



  
  return (
    jsx(
"button",
{className:"px-3 py-2 text-sm font-medium text-slate-700 bg-white border border-slate-300 rounded-lg hover:bg-slate-50 flex items-center whitespace-nowrap",onClick:on_click_7e7f04377e8df047cd26e059a1123541},
jsx(LucideBoxSelectIcon,{className:"mr-2",size:16},)
,"Prompt Toolbox"
,)
  )
}

export function Form_a8ba05ca5112ae60d1965aa3c97f928c () {
  
  const [addEvents, connectErrors] = useContext(EventLoopContext);

  
    const handleSubmit_3f8627a8162a364cd105f1ee41641d5b = useCallback((ev) => {
        const $form = ev.target
        ev.preventDefault()
        const form_data = {...Object.fromEntries(new FormData($form).entries()), ...({ ["chat_file_upload"] : getRefValue(refs["ref_chat_file_upload"]) })};

        (((...args) => (addEvents([(Event("reflex___state____state.app___states___chat_state____chat_state.send_message_from_input", ({  }), ({  })))], args, ({  }))))(ev));

        if (false) {
            $form.reset()
        }
    })
    




  
  return (
    jsx(
"form",
{className:"w-full",onSubmit:handleSubmit_3f8627a8162a364cd105f1ee41641d5b},
jsx(
"div",
{className:"flex items-end gap-2 px-4"},
jsx(Textarea_84b6d82b1dc0bca178b53ddf41f472e3,{},)
,),jsx(
"div",
{className:"flex items-center gap-2 px-4 mt-2"},
jsx(Comp_548621951a4f97ca805bc5a5102f0d51,{},)
,jsx(Button_6e75cf5bec94bc944097a17812febadd,{},)
,jsx(Button_e04019c807f87144548760b6374cdbfd,{},)
,jsx(Button_49f502aa70a8b156a29bac1e8d19b9bd,{},)
,),jsx(Fragment_de5178b50191bc21ea6c5a3095ef5e52,{},)
,)
  )
}

export function Button_49f502aa70a8b156a29bac1e8d19b9bd () {
  
  const reflex___state____state__app___states___chat_state____chat_state = useContext(StateContexts.reflex___state____state__app___states___chat_state____chat_state)





  
  return (
    jsx(
"button",
{className:"p-2.5 bg-sky-500 text-white rounded-lg hover:bg-sky-600 focus:outline-none focus:ring-2 focus:ring-sky-400 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed transition-colors flex-shrink-0 ml-auto",disabled:(reflex___state____state__app___states___chat_state____chat_state.processing || (reflex___state____state__app___states___chat_state____chat_state.input_message.trim() === ((("" && !(reflex___state____state__app___states___chat_state____chat_state.explain_active)) && !(reflex___state____state__app___states___chat_state____chat_state.tasks_active)) && (reflex___state____state__app___states___chat_state____chat_state.uploaded_file_name === "")))),type:"submit"},
jsx(Fragment_bcd124deb6d2681000ab043dd8b19699,{},)
,)
  )
}

export function Fragment_b2e04f50188f111832b038832d23832a () {
  
  const reflex___state____state__app___states___chat_state____chat_state = useContext(StateContexts.reflex___state____state__app___states___chat_state____chat_state)





  
  return (
    jsx(
Fragment,
{},
((reflex___state____state__app___states___chat_state____chat_state.messages.length > 0) ? (jsx(
Fragment,
{},
jsx(Button_03058aa5385965ed5439c2c5f45c73d6,{},)
,)) : (jsx(Fragment,{},)
)),)
  )
}

export function Button_03058aa5385965ed5439c2c5f45c73d6 () {
  
  const [addEvents, connectErrors] = useContext(EventLoopContext);


  const on_click_277dbecd287dceaa2d07bcc847ccd3ad = useCallback(((...args) => (addEvents([(Event("reflex___state____state.app___states___chat_state____chat_state.clear_messages", ({  }), ({  })))], args, ({  })))), [addEvents, Event])



  
  return (
    jsx(
"button",
{className:"mt-3 mb-1 text-xs text-slate-500 hover:text-red-500 flex items-center self-center transition-colors",onClick:on_click_277dbecd287dceaa2d07bcc847ccd3ad},
jsx(LucideTrash2,{className:"mr-1",size:14},)
,"Clear Chat"
,)
  )
}

export default function Component() {
    




  return (
    jsx(
Fragment,
{},
jsx(
RadixThemesFlex,
{align:"start",className:"rx-Stack",css:({ ["alignItems"] : "stretch", ["width"] : "100%", ["height"] : "100vh", ["background"] : "white" }),direction:"column",gap:"0"},
jsx(Flex_f9bc6248d62c14ee3f4923ca1ef51d25,{},)
,jsx(
"div",
{className:"sticky bottom-0 left-0 right-0 py-3 bg-slate-100/90 backdrop-blur-md border-t border-slate-200 flex flex-col"},
jsx(
"div",
{className:"flex flex-col sm:flex-row items-center gap-3 mb-3 px-4 pt-3"},
jsx(Button_0ec4ddd6b671297f79d185e4a7d65d33,{},)
,jsx(Div_6fcc06680e956e9456738a77d44d26ce,{},)
,),jsx(Form_a8ba05ca5112ae60d1965aa3c97f928c,{},)
,jsx(Fragment_b2e04f50188f111832b038832d23832a,{},)
,),),jsx(
NextHead,
{},
jsx(
"title",
{},
"App | Index"
,),jsx("meta",{content:"favicon.ico",property:"og:image"},)
,),)
  )
}
