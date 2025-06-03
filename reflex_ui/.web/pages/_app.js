/** @jsxImportSource @emotion/react */

import '$/styles/__reflex_global_styles.css'

import { Fragment, StrictMode, useContext } from "react"
import { ErrorBoundary } from "react-error-boundary"
import { EventLoopContext, UploadFilesProvider } from "$/utils/context"
import { Event } from "$/utils/state"
import { jsx } from "@emotion/react"
import RadixThemesColorModeProvider from "$/components/reflex/radix_themes_color_mode_provider.js"
import { Theme as RadixThemesTheme } from "@radix-ui/themes"
import theme from "$/utils/theme.js"
import { DefaultOverlayComponents, MemoizedToastProvider } from "$/utils/components"


import { EventLoopProvider, StateProvider, defaultColorMode } from "$/utils/context.js";
import { ThemeProvider } from 'next-themes'
import * as React from "react";
import * as emotion_react from "@emotion/react";
import * as utils_components from "$/utils/components";
import * as next_link from "next/link";
import * as radix_ui_themes from "@radix-ui/themes";
import * as utils_context from "$/utils/context";
import * as utils_state from "$/utils/state";


function AppWrap({children}) {
  
  const [addEvents, connectErrors] = useContext(EventLoopContext);




  return (
    jsx(
StrictMode,
{},
jsx(
ErrorBoundary,
{fallbackRender:((event_args) => (jsx("div", ({css:({ ["height"] : "100%", ["width"] : "100%", ["position"] : "absolute", ["display"] : "flex", ["alignItems"] : "center", ["justifyContent"] : "center" })}), (jsx("div", ({css:({ ["display"] : "flex", ["flexDirection"] : "column", ["gap"] : "1rem" })}), (jsx("div", ({css:({ ["display"] : "flex", ["flexDirection"] : "column", ["gap"] : "1rem", ["maxWidth"] : "50ch", ["border"] : "1px solid #888888", ["borderRadius"] : "0.25rem", ["padding"] : "1rem" })}), (jsx("h2", ({css:({ ["fontSize"] : "1.25rem", ["fontWeight"] : "bold" })}), (jsx(Fragment, ({}), "An error occurred while rendering this page.")))), (jsx("p", ({css:({ ["opacity"] : "0.75" })}), (jsx(Fragment, ({}), "This is an error with the application itself.")))), (jsx("details", ({}), (jsx("summary", ({css:({ ["padding"] : "0.5rem" })}), (jsx(Fragment, ({}), "Error message")))), (jsx("div", ({css:({ ["width"] : "100%", ["maxHeight"] : "50vh", ["overflow"] : "auto", ["background"] : "#000", ["color"] : "#fff", ["borderRadius"] : "0.25rem" })}), (jsx("div", ({css:({ ["padding"] : "0.5rem", ["width"] : "fit-content" })}), (jsx("pre", ({}), (jsx(Fragment, ({}), event_args.error.stack)))))))), (jsx("button", ({css:({ ["padding"] : "0.35rem 0.75rem", ["margin"] : "0.5rem", ["background"] : "#fff", ["color"] : "#000", ["border"] : "1px solid #000", ["borderRadius"] : "0.25rem", ["fontWeight"] : "bold" }),onClick:((...args) => (addEvents([(Event("_call_function", ({ ["function"] : (() => (navigator["clipboard"]["writeText"](event_args.error.stack))), ["callback"] : null }), ({  })))], args, ({  }))))}), (jsx(Fragment, ({}), "Copy")))))))), (jsx("hr", ({css:({ ["borderColor"] : "currentColor", ["opacity"] : "0.25" })}))), (jsx("a", ({href:"https://reflex.dev"}), (jsx("div", ({css:({ ["display"] : "flex", ["alignItems"] : "baseline", ["justifyContent"] : "center", ["fontFamily"] : "monospace", ["--default-font-family"] : "monospace", ["gap"] : "0.5rem" })}), (jsx(Fragment, ({}), "Built with ")), (jsx("svg", ({"aria-label":"Reflex",css:({ ["fill"] : "currentColor" }),height:"12",role:"img",width:"56",xmlns:"http://www.w3.org/2000/svg"}), (jsx("path", ({d:"M0 11.5999V0.399902H8.96V4.8799H6.72V2.6399H2.24V4.8799H6.72V7.1199H2.24V11.5999H0ZM6.72 11.5999V7.1199H8.96V11.5999H6.72Z"}))), (jsx("path", ({d:"M11.2 11.5999V0.399902H17.92V2.6399H13.44V4.8799H17.92V7.1199H13.44V9.3599H17.92V11.5999H11.2Z"}))), (jsx("path", ({d:"M20.16 11.5999V0.399902H26.88V2.6399H22.4V4.8799H26.88V7.1199H22.4V11.5999H20.16Z"}))), (jsx("path", ({d:"M29.12 11.5999V0.399902H31.36V9.3599H35.84V11.5999H29.12Z"}))), (jsx("path", ({d:"M38.08 11.5999V0.399902H44.8V2.6399H40.32V4.8799H44.8V7.1199H40.32V9.3599H44.8V11.5999H38.08Z"}))), (jsx("path", ({d:"M47.04 4.8799V0.399902H49.28V4.8799H47.04ZM53.76 4.8799V0.399902H56V4.8799H53.76ZM49.28 7.1199V4.8799H53.76V7.1199H49.28ZM47.04 11.5999V7.1199H49.28V11.5999H47.04ZM53.76 11.5999V7.1199H56V11.5999H53.76Z"}))), (jsx("title", ({}), (jsx(Fragment, ({}), "Reflex"))))))))))))))),onError:((_error, _info) => (addEvents([(Event("reflex___state____state.reflex___state____frontend_event_exception_state.handle_frontend_exception", ({ ["stack"] : _error["stack"], ["component_stack"] : _info["componentStack"] }), ({  })))], [_error, _info], ({  }))))},
jsx(
RadixThemesColorModeProvider,
{},
jsx(
RadixThemesTheme,
{css:{...theme.styles.global[':root'], ...theme.styles.global.body}},
jsx(
Fragment,
{},
jsx(DefaultOverlayComponents,{},)
,jsx(
UploadFilesProvider,
{},
jsx(
Fragment,
{},
jsx(MemoizedToastProvider,{},)
,jsx(
Fragment,
{},
children
,),),),),),),),)
  )
}

export default function MyApp({ Component, pageProps }) {
  React.useEffect(() => {
    // Make contexts and state objects available globally for dynamic eval'd components
    let windowImports = {
      "react": React,
      "@emotion/react": emotion_react,
      "$/utils/components": utils_components,
      "next/link": next_link,
      "@radix-ui/themes": radix_ui_themes,
      "$/utils/context": utils_context,
      "$/utils/state": utils_state,
    };
    window["__reflex"] = windowImports;
  }, []);
  return (
    jsx(ThemeProvider, {defaultTheme:defaultColorMode,attribute:"class"},
      jsx(StateProvider, {},
        jsx(EventLoopProvider, {}, 
          jsx(AppWrap, {},
            jsx(Component, pageProps)
          )
        )
      )
    )
  );
}

