import Link from "next/link";
import {forwardRef, JSXElementConstructor, useMemo, RefObject} from "react";

const Bubble:JSXElementConstructor<any> = forwardRef(function Bubble({ content }, ref) {
  const isLeft = useMemo(() => !content.isQuestion || content.processing, [content]);

  return (
    <div ref={ref  as RefObject<HTMLDivElement>} className={`block mt-4 md:mt-6 pb-[7px] clear-both max-w-[85%]  ${isLeft ? 'float-left bg-[#0E0E0E] px-4 py-3 rounded-t-xl rounded-br-xl' : 'float-right bg-[#A020F0] px-4 py-3 rounded-t-xl rounded-bl-xl'}`}>
      <div className="flex justify-end">
        <div className={`talk-bubble${isLeft ? ' left' : ''} p-2 md:p-4`}>
          {content.processing ? (
            <div className="w-4 h-4 flex gap-0.5 items-center justify-center">
              <div className="animate-pulse bg-[#efefef] rounded-full p-1" />
              <div className="animate-pulse bg-[#efefef] rounded-full p-1" />
              <div className="animate-pulse bg-[#efefef] rounded-full p-1" />
            </div>
          ) : (
            <p className="text-sm md:text-base">{content.text}</p>
          )}
          <svg width="12" height="7" viewBox="0 0 12 7" fill="#fff" xmlns="http://www.w3.org/2000/svg">
            <path d="M0.730278 0.921112C-3.49587 0.921112 12 0.921112 12 0.921112V5.67376C12 6.8181 9.9396 7.23093 9.31641 6.27116C6.83775 2.45382 3.72507 0.921112 0.730278 0.921112Z" />
          </svg>
        </div>
      </div>
    </div>
  )
})

export default Bubble;