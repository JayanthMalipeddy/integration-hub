param([ValidateSet('sample','encode')][string]$Mode = 'encode')
$ErrorActionPreference = 'Stop'
Add-Type -AssemblyName System.Drawing
Add-Type -ReferencedAssemblies System.Drawing -TypeDefinition @"
using System;
using System.IO;
using System.Drawing;
using System.Drawing.Imaging;
using System.Runtime.InteropServices;
public static class ArchitectureGif {
  static byte[] ReadPixels(string path, out int width, out int height) {
    using (var source = new Bitmap(path)) {
      width = source.Width; height = source.Height;
      using (var bmp = new Bitmap(width, height, PixelFormat.Format24bppRgb)) {
        using (var g = Graphics.FromImage(bmp)) g.DrawImageUnscaled(source, 0, 0);
        var data = bmp.LockBits(new Rectangle(0,0,width,height), ImageLockMode.ReadOnly, PixelFormat.Format24bppRgb);
        var pixels = new byte[width*height*3];
        for(int y=0;y<height;y++) Marshal.Copy(IntPtr.Add(data.Scan0,y*data.Stride), pixels,y*width*3,width*3);
        bmp.UnlockBits(data); return pixels;
      }
    }
  }
  public static void Sample(string root) {
    int w,h; File.WriteAllBytes(Path.Combine(root,"sample.bgr"),ReadPixels(Path.Combine(root,"frame-000.png"),out w,out h));
  }
  public static void Encode(string root) {
    var lut=File.ReadAllBytes(Path.Combine(root,"lut.bin"));
    var palette=File.ReadAllBytes(Path.Combine(root,"palette.bin"));
    byte[] previous=null;
    using(var manifest=new StreamWriter(Path.Combine(root,"frames.csv"))) {
      for(int i=0;i<100;i++) {
        int w,h;var rgb=ReadPixels(Path.Combine(root,String.Format("frame-{0:000}.png",i)),out w,out h);
        var indices=new byte[w*h]; int left=w,top=h,right=-1,bottom=-1;
        for(int p=0;p<indices.Length;p++) {
          int q=p*3; indices[p]=lut[((rgb[q+2]>>2)<<12)|((rgb[q+1]>>2)<<6)|(rgb[q]>>2)];
          if(previous==null||indices[p]!=previous[p]) {int x=p%w,y=p/w;left=Math.Min(left,x);right=Math.Max(right,x);top=Math.Min(top,y);bottom=Math.Max(bottom,y);}
        }
        if(right<0){left=top=right=bottom=0;}
        int cw=right-left+1,ch=bottom-top+1;
        using(var bmp=new Bitmap(cw,ch,PixelFormat.Format8bppIndexed)) {
          var colors=bmp.Palette;
          for(int c=0;c<256;c++) colors.Entries[c]=Color.FromArgb(c==0?0:255,palette[c*3],palette[c*3+1],palette[c*3+2]);
          bmp.Palette=colors;
          var data=bmp.LockBits(new Rectangle(0,0,cw,ch),ImageLockMode.WriteOnly,PixelFormat.Format8bppIndexed);
          var row=new byte[data.Stride];
          for(int y=0;y<ch;y++) {
            Array.Clear(row,0,row.Length);
            for(int x=0;x<cw;x++){int p=(top+y)*w+left+x;row[x]=(previous!=null&&indices[p]==previous[p])?(byte)0:indices[p];}
            Marshal.Copy(row,0,IntPtr.Add(data.Scan0,y*data.Stride),row.Length);
          }
          bmp.UnlockBits(data);bmp.Save(Path.Combine(root,String.Format("encoded-{0:000}.gif",i)),ImageFormat.Gif);
        }
        manifest.WriteLine(String.Format("{0},{1},{2},{3},{4}",i,left,top,cw,ch));previous=indices;
        if(i%20==0) Console.WriteLine("Encoded frame {0}/100",i+1);
      }
    }
  }
}
"@
$renderRoot = [IO.Path]::GetFullPath((Join-Path $PSScriptRoot '../../runtime/architecture-animation'))
if ($Mode -eq 'sample') { [ArchitectureGif]::Sample($renderRoot) } else { [ArchitectureGif]::Encode($renderRoot) }
