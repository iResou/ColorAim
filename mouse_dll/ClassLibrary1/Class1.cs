using InputInterceptorNS;
using System;
using System.Runtime.InteropServices;

namespace ClassLibrary1
{
    public class Class1
    {
        public void move_mouse(float x, float y, int box_size, float m, float y_diff, int smoothing)
        {
            if (InputInterceptor.Initialize())
            {
                // for x-coords
                float xr;
                if (x > box_size)
                {
                    xr = -(960 - x);
                    if ((xr + 960) > 1920)
                    {
                        xr = 0;
                    }
                } else
                {
                    xr = x;
                }
                // for y-coords
                float yr;
                if (y > box_size)
                {
                    yr = -(540 - y);
                    if ((yr + 540) > 1080)
                    {
                        yr = 0;
                    }
                }
                else
                {
                    yr = y;
                }
                int xf = (int)(xr * m);
                int yf = (int)((yr - y_diff) * m);
                // int moveX = xf / smoothing;
                // int moveY = yf / smoothing;
                MouseHook mouseHook = new MouseHook();
                /* int max = smoothing + 1;
                for (int i = 0; i < max; i++)
                {
                    mouseHook.MoveCursorBy(moveX, moveY, false);
                } */
                mouseHook.MoveCursorBy(xf, yf, false);
                // mouseHook.SimulateLeftButtonClick(50);
            }
        }

        public void click_mouse()
        {
            MouseHook mouseHook=new MouseHook();
            mouseHook.SimulateLeftButtonClick(1);

        }
        [DllImport("user32.dll")]
        static extern short GetAsyncKeyState(int VirtualKeyPressed);
        public static bool is_activated(int key)
        {
            if (GetAsyncKeyState(key) == 0)
                return false;
            else
                return true;
        }
        public bool Check(float a, int b)
        {
            if (a > b)
            {
                return true;
            } 
            else
            {
                return false;
            }
        }
    }
}
