param(
    [Parameter(Mandatory = $true)]
    [string]$ProfileSlug
)

$ErrorActionPreference = 'Stop'

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$killScript = Join-Path $scriptDir 'kill-kiosk-browser.ps1'
$pidFile = Join-Path $env:TEMP "activerse-kiosk-listener-$ProfileSlug.pid"
[System.IO.File]::WriteAllText($pidFile, $PID.ToString())

Add-Type @"
using System;
using System.Drawing;
using System.Diagnostics;
using System.Runtime.InteropServices;
using System.Windows.Forms;

public class ActiverseKioskExitForm : Form {
    public const int WM_HOTKEY = 0x0312;
    public const uint MOD_CONTROL = 0x0002;
    public const uint MOD_SHIFT = 0x0004;
    public const int HOTKEY_ID = 1;
    public const int VK_K = 0x4B;

    [DllImport("user32.dll")]
    public static extern bool RegisterHotKey(IntPtr hWnd, int id, uint fsModifiers, uint vk);

    [DllImport("user32.dll")]
    public static extern bool UnregisterHotKey(IntPtr hWnd, int id);

    public string KillScriptPath { get; set; }
    public string Profile { get; set; }

    public ActiverseKioskExitForm(string title) {
        Text = title;
        ShowInTaskbar = false;
        FormBorderStyle = FormBorderStyle.FixedToolWindow;
        StartPosition = FormStartPosition.Manual;
        Location = new Point(-32000, -32000);
        Size = new Size(1, 1);
    }

    protected override void OnHandleCreated(EventArgs e) {
        base.OnHandleCreated(e);
        if (!RegisterHotKey(Handle, HOTKEY_ID, MOD_CONTROL | MOD_SHIFT, VK_K)) {
            throw new InvalidOperationException("RegisterHotKey failed");
        }
    }

    protected override void OnFormClosing(FormClosingEventArgs e) {
        UnregisterHotKey(Handle, HOTKEY_ID);
        base.OnFormClosing(e);
    }

    protected override void WndProc(ref Message m) {
        if (m.Msg == WM_HOTKEY) {
            try {
                var psi = new ProcessStartInfo {
                    FileName = "powershell.exe",
                    Arguments = string.Format("-NoProfile -ExecutionPolicy Bypass -File \"{0}\" -ProfileSlug \"{1}\"", KillScriptPath, Profile),
                    UseShellExecute = false,
                    CreateNoWindow = true
                };
                Process.Start(psi);
            } catch {
            }
            BeginInvoke((Action)(() => Close()));
            return;
        }
        base.WndProc(ref m);
    }
}
"@

$form = New-Object ActiverseKioskExitForm "Activerse Kiosk Exit - $ProfileSlug"
$form.KillScriptPath = $killScript
$form.Profile = $ProfileSlug

$form.Add_Load({
    $form.Hide()
})

$form.Add_FormClosed({
    if (Test-Path $pidFile) {
        Remove-Item $pidFile -Force -ErrorAction SilentlyContinue
    }
})

try {
    [void][System.Windows.Forms.Application]::Run($form)
} finally {
    if (Test-Path $pidFile) {
        Remove-Item $pidFile -Force -ErrorAction SilentlyContinue
    }
}
